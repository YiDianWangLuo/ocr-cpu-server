from paddleocr import PaddleOCR, draw_ocr
from pdf2image import convert_from_path
import os, cv2, numpy as np
import logging
import datetime

pdf_folder = './pdf/'
img_folder = './img'
pdfoutputimg_folder_all = './pdftoimg_all'
pdfoutputimg_folder_cover = './pdftoimg_cover'
pdfoutputimg_folder_note = './pdftoimg_note'
pdfoutputimg_folder_main = './pdftoimg_main'
pdfoutputimg_binary_folder_main = './pdftoimg_binary_main'
pdfoutputimg_folder_appendix = './pdftoimg_appendix'
outputfile_folder = './outputfile'
outputlog_folder = './outputlog'
outputimg_folder = './outputimg'
outputimg_binary_folder = './outputbinaryimg'


if not os.path.exists(outputimg_folder):
    os.makedirs(outputimg_folder)

if not os.path.exists(outputfile_folder):
    os.makedirs(outputfile_folder)


for root, dirs, files in os.walk(pdf_folder):
    # do pdf to image
    for filename in files:
        if filename.endswith('.pdf'):
            file_path = os.path.join(root, filename)
            pages = convert_from_path(file_path,
                                    dpi=300
                                    #,grayscale = True
                                    )
            # 保存圖像
            for i, page in enumerate(pages):
                # print(filename+" page"+str(i)+" w:"+str(page.size[0]))#PDF頁面的寬度
                # print(filename+" page"+str(i)+" h:"+str(page.size[1]))#PDF頁面的高度
                # output_path = os.path.join(pdfoutputimg_folder_all, f'{filename}_page_{i+1}.jpg')

                filename = os.path.splitext(filename)[0]
                # 依據頁面寬進行文本分類，寬<1000為note、2000<寬<2400為正文、2400<寬<3000為封面、寬>4000為附錄
                if page.size[0] < 2000:
                    output_path = os.path.join(pdfoutputimg_folder_note, f'{filename}_page_{i+1}_note.jpg')
                    page.save(output_path, 'JPEG')
                elif page.size[0] > 2000 and page.size[0] < 2400 :
                    output_path = os.path.join(pdfoutputimg_folder_main, f'{filename}_page_{i+1}_main.jpg')
                    page.save(output_path, 'JPEG')
                if page.size[0] > 2400 and page.size[0] < 3000 :
                    output_path = os.path.join(pdfoutputimg_folder_cover, f'{filename}_page_{i+1}_cover.jpg')
                    page.save(output_path, 'JPEG')
                else:
                    output_path = os.path.join(pdfoutputimg_folder_appendix, f'{filename}_page_{i+1}.jpg')
                    page.save(output_path, 'JPEG')

# 配置 logging
logging.basicConfig(level=logging.INFO, # 設置log级别为 INFO
                    format ='%(aㄅsctime)s - %(levelname)s - %(message)s' # 设置日志格式
                    )

# create logFileHandler
log_filename = datetime.datetime.now().strftime("%Y-%m-%d.log")#-%M-%S
log_path = os.path.join(outputlog_folder, log_filename)

# 指定log路径和檔名
log_dir = os.path.dirname(log_path)
if not os.path.exists(log_dir):
   os.makedirs(log_dir)

file_handler = logging.FileHandler(log_path) #log_path)
file_handler.setLevel(logging.ERROR)

# 將 FileHandler 添加到 logger
logger = logging.getLogger()
logger.addHandler(file_handler)
logger.error('-------------log start------------------')


# do ocr (stage1以本文為主)
for filename in os.listdir(pdfoutputimg_folder_main):
    # print(filename)
    # print(img_folder+'/'+filename)

    ocr = PaddleOCR(use_angle_cls=True, lang='ch')#, rec_algorithm = 'chinese_cht') # need to run only once to download and load model into memory
    img_path = pdfoutputimg_folder_main+"/"+filename #'PaddleOCR/doc/imgs_en/img_12.jpg'
    # img_path = './img/4-1.jpeg'

    # cv2.imread(img_path)
    # cv_img = cv2.cvtColor(np.asarray(img_path), cv2.COLOR_RGB2BGR)
    # gray_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    # ret, bin_img = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    #prepare output ocr result 
    result = ocr.ocr(img_path, cls=True)

    logger.error(filename)
    logger.error('--------------filestart-----------------')


    for idx in range(len(result)):
        res = result[idx]
        for line in res:
            # print(line)
            # record log
            # print_obj = str(line)22
            #print(print_obj)
            logger.error(str(line))
    logger.error('---------------fileend----------------')
    # 去掉副檔名
    filename = os.path.splitext(filename)[0]

    # draw result
    from PIL import Image
    result = result[0]
    image = Image.open(img_path).convert('RGB')
    boxes = [line[0] for line in result]
    print('---------------------------')
    # print(boxes)
    txts = [line[1][0] for line in result]
    scores = [line[1][1] for line in result]
    #im_show = draw_ocr(image, boxes, txts, scores, font_path='./PaddleOCR/doc/fonts/simfang.ttf')
    im_show = draw_ocr(image, boxes, txts, scores, font_path='./doc/fonts/chinese_cht.ttf')
    im_show = Image.fromarray(im_show)
    im_show.save(os.path.join(outputimg_folder, f'{filename}_result.jpg'))

     # save to file
    righttop_location = [topright[2] for topright in boxes]
    # right to left order [right][top]
    righttop_order = [sorted(righttop_location,reverse=True)]

    # save to file
    righttop_location = [topright[2] for topright in boxes]
    # right to left order [right][top]
    righttop_order = [sorted(righttop_location,reverse=True)]

    # 搭配 with 寫入檔案
    outputresultfile = filename.split("_page")[0]
    # print(outputresultfile)
    output_path = os.path.join(outputfile_folder, f'{outputresultfile}_binary.txt')
    if os.path.exists(output_path):
        mode = 'a'  # 如果檔案存在，使用附加模式
    else:
        mode = 'w'  # 如果檔案不存在，使用寫入模式

    with open(output_path, mode) as f:
        # get each box righttop(x, y)
        for righttop in righttop_order[0]:
            for line in result:
                # print(righttop)
                
                # check if match the righttop(x, y)
                if line[0][2] == righttop:
                    # write file
                    f.write(line[1][0]+'\n')
                    break
            else:
                continue
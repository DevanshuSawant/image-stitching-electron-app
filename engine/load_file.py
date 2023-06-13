import cv2
import numpy as np
import matplotlib.pyplot as plt
import imageio
import os
from csv import writer

import imgstitch as ims 

PATH = "assets/Untitled design/"

def load_files(filename):

    trainImg = []
    trainImg_gray = []

    for file in filename:
        trainImg.append(cv2.imread(file))
        print('LOADED: ', file)

    # IF PATH IS GIVEN
    # for image in os.listdir(PATH):
    #     if image.endswith(".jpg"):
    #         file_path = PATH + image
    #         print('LOADED: ',file_path)
    #     trainImg.append(cv2.imread(file_path))

    #converting all images from bgr to rgb and then appending those 
    #images to grayscale in another list.
    for i in range(len(trainImg)):
        trainImg[i] = cv2.cvtColor(trainImg[i], cv2.COLOR_BGR2RGB)
        trainImg_gray.append(cv2.cvtColor(trainImg[i], cv2.COLOR_RGB2GRAY))
    
    #calling function to assign 1st image of the list to last+1 index of the 
    #list where all the stotched images will be kept.
    ims.lastimg(trainImg, trainImg_gray)

    #calling function to create a while loop to stitch image and returning final 
    #stitched image for saving out of current folder of used images.
    finalImg = ims.loops(trainImg, trainImg_gray)
    
    #saving final image out of folder
    os.chdir('assets')
    imageio.imwrite('stitchedResult-2.bmp', finalImg)


# if __name__=="__main__":
#     main()
    

def storeMatrixData(fileNames, homographyMatrix):

    # df = pd.DataFrame({
    #     'image1': [fileNames[0]],
    #     'image2': [fileNames[1]],
    #     'h11': [homographyMatrix[0][0]],
    #     'h12': [homographyMatrix[0][1]],
    #     'h13': [homographyMatrix[0][2]],
    #     'h21': [homographyMatrix[1][0]],
    #     'h22': [homographyMatrix[1][1]],
    #     'h23': [homographyMatrix[1][2]],
    #     'h31': [homographyMatrix[2][0]],
    #     'h32': [homographyMatrix[2][1]]
    #     })
    
    dataList = [fileNames[0], fileNames[1], 
                homographyMatrix[0][0], homographyMatrix[0][1], homographyMatrix[0][2],
                homographyMatrix[1][0], homographyMatrix[1][1], homographyMatrix[1][2],
                homographyMatrix[2][0], homographyMatrix[2][1] ]
 
    with open('matrix-data-analysis.csv', 'a') as f_object:
        writer_object = writer(f_object)
        writer_object.writerow(dataList)
        f_object.close()
        print('done')
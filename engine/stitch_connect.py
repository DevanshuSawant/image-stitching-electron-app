import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

import custom_stitch as cust

def getStitchResult(filenames):

    # PATH = 'assets/SMT-scratch/original/'
    
    feature_extractor = 'sift'

    imageBucket = []
    resultImageBucket = []

    for file in filenames:
        imageBucket.append(cv2.imread(file))

    while True:
        if len(imageBucket) < 2:
            break
        else:
            image1 = imageBucket.pop(0)
            image1_gray = cv2.cvtColor(image1, cv2.COLOR_RGB2GRAY)

            image2 = imageBucket.pop(0)
            image2_gray = cv2.cvtColor(image2, cv2.COLOR_RGB2GRAY)

            # fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, constrained_layout=False, figsize=(16,9))
            # ax1.imshow(image1, cmap="gray")
            # ax1.set_xlabel("Query image", fontsize=14)

            # ax2.imshow(image2, cmap="gray")
            # ax2.set_xlabel("Train image (Image to be transformed)", fontsize=14)

            # plt.show()

            widthSize = min(image1.shape[1], image2.shape[1])
            kpsA, featuresA = cust.detectAndDescribe(image2_gray,'left', widthSize, method=feature_extractor)
            kpsB, featuresB = cust.detectAndDescribe(image1_gray, 'right', widthSize, method=feature_extractor)

            # fig, (ax1,ax2) = plt.subplots(nrows=1, ncols=2, figsize=(20,8), constrained_layout=False)
            # ax1.imshow(cv2.drawKeypoints(image2_gray,kpsA,None,color=(0,255,0)))
            # ax1.set_xlabel("(a)", fontsize=14)
    
            # ax2.imshow(cv2.drawKeypoints(image1_gray,kpsB,None,color=(0,255,0)))
            # ax2.set_xlabel("(b)", fontsize=14)

            # plt.show()

            # fig = plt.figure(figsize=(20,8))
    
            matches = cust.matchKeyPointsKNN(featuresA, featuresB, ratio=0.73, method=feature_extractor)

            img3 = cv2.drawMatches(image2,kpsA,image1,kpsB,matches,
                           None,flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    
            # plt.imshow(img3)
            # plt.show()

            M = cust.getHomography(kpsA, kpsB, featuresA, featuresB, matches, reprojThresh=4)
            if M is None:

                print("Error!")
                print('Storing in Buffer')

                resultImageBucket.append(image1)
                imageBucket.insert(0, image2)
                continue
        
            (matches, H, status) = M

            width = image2.shape[1] + image1.shape[1]
            height = max(image2.shape[0], image1.shape[0])

            result = cv2.warpPerspective(image2, H, (width-100, height))
            result[0:image1.shape[0], 0:image1.shape[1]] = image1

            result = cust.removeBlackBg(result)
            
            # plt.figure(figsize=(20,10))
            # plt.imshow(result)
            # plt.show()

            imageBucket.insert(0, result)
    
    print(f'Image Bucket => {len(imageBucket)}')
    print(f'Image Resultant Bucket => {len(resultImageBucket)}')
    for index,image in enumerate(imageBucket):
        cv2.imwrite(f'image{index}.png',image)

    for index,image in enumerate(resultImageBucket):
        cv2.imwrite(f'result-image{index}.png',image)

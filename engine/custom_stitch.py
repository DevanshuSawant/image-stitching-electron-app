import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def detectAndDescribe(image, ort, widthSize, method=None):

    assert method is not None

    # detect and extract features from the image
    descriptor = cv2.xfeatures2d.SIFT_create()

    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    w = image.shape[1]
    # w = widthSize
    half = round(widthSize / 2)
    # half = 114 in some cases
    # use half * 2 in some cases

    if ort == 'right':
        cv2.rectangle(mask, (w, 0), (w - (half), image.shape[0]), (255), thickness=-1)
    elif ort == 'left':
        cv2.rectangle(mask, (0, 0), ((half), image.shape[0]), (255), thickness=-1)

    # get keypoints and descriptors
    (kps, features) = descriptor.detectAndCompute(image, mask)
    
    return (kps, features)

def createMatcher(method,crossCheck):
    # "Create and return a Matcher Object"
    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=crossCheck)
    return bf

def matchKeyPointsKNN(featuresA, featuresB, ratio, method):
    bf = createMatcher(method, crossCheck=False)
    # compute the raw matches and initialize the list of actual matches
    rawMatches = bf.knnMatch(featuresA, featuresB, 2)
    matches = []

    # loop over the raw matches
    for m,n in rawMatches:
        # ensure the distance is within a certain ratio of each
        # other (i.e. Lowe's ratio test)
        if m.distance < n.distance * ratio:
            matches.append(m)
    return matches

def getHomography(kpsA, kpsB, featuresA, featuresB, matches, reprojThresh):
    # convert the keypoints to numpy arrays
    kpsA = np.float32([kp.pt for kp in kpsA])
    kpsB = np.float32([kp.pt for kp in kpsB])
    
    if len(matches) > 4:

        # construct the two sets of points
        ptsA = np.float32([kpsA[m.queryIdx] for m in matches])
        ptsB = np.float32([kpsB[m.trainIdx] for m in matches])
        
        # estimate the homography between the sets of points
        (H, status) = cv2.findHomography(ptsA, ptsB, cv2.RANSAC,
            reprojThresh)
        
        inlinerCount = 0

        for stat in status:
            if stat[0] == 1: inlinerCount += 1
        
        print(f'{len(status)} => inliner-count: {inlinerCount}')
        
        if len(status) < 32 or inlinerCount <= len(status) / 5:
            return None

        return (matches, H, status)
    else:
        return None

def removeBlackBg(imageFile):
    gray = cv2.cvtColor(imageFile, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 3)

    ret, thresh = cv2.threshold(gray, 1, 255, 0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    max_area = -1
    best_cnt = None

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > max_area:
            max_area = area
            best_cnt = cnt

    approx = cv2.approxPolyDP(best_cnt, 0.01 * cv2.arcLength(best_cnt, True), True)
    far = approx[np.product(approx, 2).argmax()][0]

    xmax = max([val for sublist in approx[:, :, 0] for val in sublist])
    x = min(far[0], xmax)

    # ymax = max([val for sublist in approx[:, :, 1] for val in sublist])
    # y = min(far[1], ymax)

    imageBgRem = imageFile[:, :x].copy()
    # print(contours, x, y)

    return imageBgRem

import cv2
import numpy as np
import matplotlib.pyplot as plt
import imageio
import os


feature_extractor = 'sift'
feature_matching = 'knn'
matches_threshold_ratio = 5

kps = []
features = []
i = 0
j = 0


# function to append first image of the list to the back of the list
# where all the stitched images will be stored.
def lastimg(trainImg, trainImg_gray):
    j = len(trainImg)
    # print(j)
    trainImg.append(trainImg[0])
    trainImg_gray.append(cv2.cvtColor(trainImg[j], cv2.COLOR_RGB2GRAY))

    plt.imshow(trainImg_gray[j], cmap="gray")
    plt.show()


# function for feature extraction.
def detectAndDescribe(image, ort):
    # detect and extract features from the image
    descriptor = cv2.xfeatures2d.SIFT_create(10000)

    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    w = image.shape[1]
    batch = round(w / 14)

    if ort == 'right':
        cv2.rectangle(mask, (w, 0), (w - (batch * 2), image.shape[0]), (255), thickness=-1)
    elif ort == 'left':
        cv2.rectangle(mask, (0, 0), ((batch * 2), image.shape[0]), (255), thickness=-1)
    # # image = sgmtImage.segmentImage(image, ort)

    # get keypoints and descriptors
    (kps, features) = descriptor.detectAndCompute(image, mask)

    return (kps, features)


# function for brute force matching
def matchKeyPointsBF(featuresA, featuresB):
    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
    best_matches = bf.match(featuresA, featuresB)

    # rawMatches = sorted(best_matches, key = lambda x:x.distance)
    print("Raw matches:", len(best_matches))

    best_matches = sorted(best_matches, key=lambda x: x.distance, reverse=False)
    total_matches = len(best_matches)

    # incr = 0
    # while True:
    #     if matches_threshold_ratio - incr <= 0:
    #         break
    #     curr_len = int(total_matches / (matches_threshold_ratio - incr))
    #     if curr_len < 100 or curr_len == total_matches:
    #         incr += 1
    #     else:
    #         break

    # goodMatches = curr_len
    best_matches = best_matches
    print("Best matches within Threshold:", len(best_matches))

    return best_matches

def matchKeyPointsKNN(featuresA, featuresB, ratio, method):
    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
    # compute the raw matches and initialize the list of actual matches
    rawMatches = bf.knnMatch(featuresA, featuresB, 2)
    print("Raw matches (knn):", len(rawMatches))
    matches = []

    # loop over the raw matches
    for m,n in rawMatches:
        # ensure the distance is within a certain ratio of each
        # other (i.e. Lowe's ratio test)
        if m.distance < n.distance * ratio:
            matches.append(m)
    return matches


# function to get homography matrix.
def getHomography(kpsA, kpsB, featuresA, featuresB, matches, reprojThresh):
    # convert the keypoints to numpy arrays
    kpsA = np.float32([kp.pt for kp in kpsA])
    kpsB = np.float32([kp.pt for kp in kpsB])

    if len(matches) > 4:
        # construct the two sets of points
        ptsA = np.float32([kpsA[m.queryIdx] for m in matches])
        ptsB = np.float32([kpsB[m.trainIdx] for m in matches])

        # estimate the homography between the sets of points
        (H, status) = cv2.findHomography(ptsA, ptsB, cv2.RANSAC, reprojThresh)
 
        return (matches, H, status)

    else:
        return None


# function to create while loop to go through the list
# of images and stitch them in order.
def loops(trainImg, trainImg_gray):
    i = 1
    while (i < len(trainImg) - 1):
        kpsA, featuresA = detectAndDescribe(trainImg_gray[i], 'left')
        kpsB, featuresB = detectAndDescribe(trainImg_gray[j], 'right')
        # print(kpsA)

        print("Using: {} feature matcher".format(feature_matching))

        # matches = matchKeyPointsBF(featuresA, featuresB)

        # new_matches = []
        # sum_for_avg = 0
        # avg_diff_threshold = 0

        # for match in matches:
        #     p1 = kpsA[match.queryIdx].pt
        #     p2 = kpsB[match.trainIdx].pt
        #     # print(p1, p2)
        #     sum_for_avg += abs(p1[1] - p2[1])

        # avg_diff_threshold = sum_for_avg / len(matches)

        # for match in matches:
        #     p1 = kpsA[match.queryIdx].pt
        #     p2 = kpsB[match.trainIdx].pt
        #     if abs(p1[1] - p2[1]) < 150:
        #         new_matches.append(match)

        # print('Better matches based on positional difference: ', len(new_matches))

        matches = matchKeyPointsKNN(featuresA, featuresB, ratio=0.75, method=feature_extractor)
        img3 = cv2.drawMatches(trainImg[i],kpsA,trainImg[j],kpsB,np.random.choice(matches,100),
                           None,flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

        # img3 = cv2.drawMatches(trainImg[i], kpsA, trainImg[j], kpsB, new_matches,
        #                        None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

        plt.imshow(img3)
        plt.axis('off')
        plt.show()

        M = getHomography(kpsA, kpsB, featuresA, featuresB, new_matches, reprojThresh=4)
        if M is None:
            print("Error!")
        (matches, H, status) = M

        print(H)

        new_matches = []
        # Apply a horizontal panorama
        width = trainImg[j].shape[1] + trainImg[i].shape[1]
        height = max(trainImg[j].shape[0], trainImg[i].shape[0])
        # otherwise, apply a perspective warp to stitch the images
        # together

        # result = np.zeros((height,width,3), np.uint8)
        result = cv2.warpPerspective(trainImg[i], H, (width, height))
        plt.figure(figsize=(20,10))
        plt.imshow(result)

        plt.axis('off')
        plt.show()

        result[0:trainImg[j].shape[0], 0:trainImg[j].shape[1]] = trainImg[j]

        # w = trainImg[j].shape[1]
        # batch = round(w / 12) 

        trainImg[j] = removeBlackBg(result)
        # trainImg[j] = result
        trainImg_gray[j] = cv2.cvtColor(trainImg[j], cv2.COLOR_RGB2GRAY)

        # plt.figure(figsize=(20,10))
        # plt.imshow(result)

        # plt.axis('off')
        # plt.show()

        i += 1
        
    # plt.figure(figsize=(20,10))
    # plt.axis('off')
    # plt.imshow(result)

    # #imageio.imwrite(str(j+10)+'234.jpeg', result)
    # plt.get_current_fig_manager().window.state('zoomed')
    # plt.subplots_adjust(left=0.112, bottom=0.17, top=1, right=0.7)
    # plt.show()

    return removeBlackBg(trainImg[j])


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

# cv2.imshow('image', img2)
# cv2.waitKey(0)


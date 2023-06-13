import cv2
import numpy as np
import os

from upload_multiple import uploadWindow

def getEdgeConnectCoordinates(img):
    kernel = np.ones((5, 5), np.uint8)
    img_dilation = cv2.dilate(img, kernel, iterations=1)  

    t_lower = 150  # Lower Threshold
    t_upper = 300 # Upper threshold
    edges = cv2.Canny(img_dilation, t_lower, t_upper)
    cv2.imshow("edge-img", edges)
    cv2.waitKey(0)
    
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)

    longest_edges = []
    coordinates = []
    y_coordinates = []

    # Loop over the lines and find the longest one
    if lines is None:
        print('Continuous Edge Cannot be detected in current image')
        descision = input('Continue? (Y/N)')
        if descision == 'N':
            return 0
        else:
            return 1
        
    for line in lines:
        x1, y1, x2, y2 = line[0]
        length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        if len(longest_edges) < 2:
            longest_edges.append(length)
            y_coordinates.append(y1)
            coordinates.append((x1, y1, x2, y2))
        else: 
            for curr_length in longest_edges:
                if curr_length < length:
                    index = longest_edges.index(curr_length)
                    longest_edges.remove(curr_length)
                    y_coordinates.pop(index)
                    coordinates.pop(index)

                    longest_edges.append(length)
                    y_coordinates.append(y1)
                    coordinates.append((x1, y1, x2, y2))

    # print("Marked Edges:", longest_edges)
    print("The y coordinates:", y_coordinates)
    for coordinate in coordinates:
        cv2.line(img, (coordinate[0], coordinate[1]), (coordinate[2], coordinate[3]),(0,0,255),2)
    cv2.imshow("edge-img", img)
    cv2.waitKey(0)

    return y_coordinates


def nonOverlapStitch(image1, image2):
    # img_1 = cv2.imread(imagePath1)
    # img_1 = cv2.resize(img_1, (round(img_1.shape[1] / 3), round(img_1.shape[0] / 3)))
    img_coordinates_1 = getImagefromPath(image1)
    img_coordinates_2 = getImagefromPath(image2)

    if img_coordinates_1 == 0 or img_coordinates_2 == 0:
        exit()
    elif img_coordinates_1 == 1 or img_coordinates_2 == 1:
        return

    diffVal = 100 
    for imgCoordinate in sorted(img_coordinates_1):
        for imgCoordinate2 in sorted(img_coordinates_2):
            curr_diff = abs(imgCoordinate - imgCoordinate2)
            if curr_diff < diffVal:
                diffVal = curr_diff
                minPt1 = imgCoordinate
                minPt2 = imgCoordinate2

    print(image1.shape, image2.shape, 'size-check')
    # diffVal = abs(min(img_coordinates_1) - min(img_coordinates_2))

    if minPt1 - minPt2 < minPt2 - minPt1:
        constant = cv2.copyMakeBorder(image1, diffVal, 0, 0, 0, cv2.BORDER_REPLICATE, value=[0,0,0])
        image1 = constant[0: constant.shape[0] - diffVal]

    else:
        constant = cv2.copyMakeBorder(image2, diffVal, 0, 0, 0, cv2.BORDER_REPLICATE, value=[0,0,0])
        image2 = constant[0: constant.shape[0] - diffVal]

    im_h = cv2.hconcat([image1, image2])
    return im_h
    # cv2.imwrite("joint-final-img.png", im_h)


# for i in range(7):
#     path1 = 'assets/scratch/' + (179 + i) + 'bmp'
#     path2 = 'assets/scratch/' + (179 + i + 1) + 'bmp'

# MAIN CALL FROM HERE
# nonOverlapStitch('assets/scratch/184.bmp', 'assets/scratch/185.jpg')

def getImagefromPath(image):
    image = cv2.resize(image, (round(image.shape[1] / 3), round(image.shape[0] / 3)))
    return getEdgeConnectCoordinates(image)


if __name__ == '__main__':
    # uploadWindow()
    PATH = 'assets/scratch/'

    imageBucket = []
    resultImageBucket = []

    for image in os.listdir(PATH):
        if image.endswith(".bmp"):
            file_path = PATH + image
            print('LOADED: ',file_path)
        imageBucket.append(cv2.imread(file_path))
    
    while True:
        if len(imageBucket) < 2:
            break
        else:
            image1 = imageBucket.pop(0)
            image2 = imageBucket.pop(0)
            print('here')

            result = nonOverlapStitch(image1, image2)

            if result is None:
                resultImageBucket.append(image1)
                imageBucket.insert(0, image2)
                continue
           
            imageBucket.insert(0, result)
    

    cv2.imwrite("joint-final-img.png", imageBucket[0])
    print(f'Image Bucket => {len(imageBucket)}')
    print(f'Image Resultant Bucket => {len(resultImageBucket)}')

    
    

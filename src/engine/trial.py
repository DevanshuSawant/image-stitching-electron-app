import cv2

image1 = cv2.imread('C:/Users/dusng/Documents/GitHub/image-stitching-electron-app/result-images-history/20230629152912_image1.png')

image_final = cv2.addWeighted(image1, 0.5, image1, 0.5, 25)
cv2.imwrite('C:/Users/dusng/Desktop/20230629152912_image1.png',image_final)
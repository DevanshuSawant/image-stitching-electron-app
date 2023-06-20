import cv2
import os
import glob
import sys

import custom_stitch as cust


def delete_images(folder_path):
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif']  # Add any other image extensions you want to delete

    # Generate a list of all image files in the folder
    image_files = []
    for extension in image_extensions:
        image_files.extend(glob.glob(os.path.join(folder_path, extension)))

    # Delete each image file
    for image_file in image_files:
        os.remove(image_file)
        # print(f"Deleted {image_file}")
        
save_folder = 'result-images'
# directory = os.path.dirname(os.path.abspath(save_folder))
# final_directory = os.path.join(directory,save_folder)
# print(final_directory)
# sys.stdout.flush()

def getStitchResult(filenames):
    save_folder2 = "image1.png"
    save_folder1 = 'result-images\image1.png'

    directory = os.path.dirname(os.path.abspath(save_folder1))
    final_directory1 = os.path.join(directory,save_folder2)
    print(f'finished:{final_directory1}') # final directory where the result image will be stored
    sys.stdout.flush()
    save_folder = 'result-images'
    directory = os.path.dirname(os.path.abspath(save_folder))
    final_directory = os.path.join(directory,save_folder)
    # final_directory_modified = final_directory.replace("\\", "")
    print(f'fd:{final_directory}') # final directory where the result image will be stored
    sys.stdout.flush()
    error_message = 0
    # PATH = 'assets/SMT-scratch/original/'
    
    feature_extractor = 'sift'

    imageBucket = []
    resultImageBucket = []
    number_of_images = len(filenames)
    current_number_of_completed_images = 0
    print(f'tn:{number_of_images}') # total no of images sent to js file
    sys.stdout.flush()
    
    for file in filenames:
        imageBucket.append(cv2.imread(file))
        print(file)
        sys.stdout.flush()


    while True:
        if len(imageBucket) < 2:
            current_number_of_completed_images += 1
            print(f'cd:{current_number_of_completed_images}') # current number of images currently processed if no of images are less than 2
            sys.stdout.flush()
            
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
            current_number_of_completed_images += 1
            M = cust.getHomography(kpsA, kpsB, featuresA, featuresB, matches, reprojThresh=4)
            if M is None:

                # print("Error!")
                # print('Storing in Buffer')
                error_message = 1
                resultImageBucket.append(image1)
                imageBucket.insert(0, image2)
                print(f'cd:{current_number_of_completed_images}') # current number of images currently processed if error occurs
                sys.stdout.flush()
                
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
            print(f'cd:{current_number_of_completed_images}') # current number of images currently processed if no error occurs and merged successfully
            sys.stdout.flush()
            
            imageBucket.insert(0, result)
        
         
    # print(f'Image Bucket => {len(imageBucket)}')
    # print(f'Image Resultant Bucket => {len(resultImageBucket)}')
    # for index,image in enumerate(imageBucket):
    #     cv2.imwrite(f'image{index}.png',image)

    # for index,image in enumerate(resultImageBucket):
    #     cv2.imwrite(f'result-image{index}.png',image)

    # Create the directory
    os.makedirs(final_directory, exist_ok=True)
    delete_images(save_folder)
    # Save all images together
    buckets = [resultImageBucket, imageBucket]
    final_index = 0
    # path = os.path.abspath(save_folder)
    # directory = os.path.dirname(path)
    # print(os.path.join(directory,save_folder))
    for i in range(len(buckets)):
        for index, image in enumerate(buckets[i]):
            if i == 0:
                filename = os.path.join(save_folder, f'image{index}.png')
                cv2.imwrite(filename, image)
                final_index = index
            elif i == 1:
                final_index += (index + 1)
                filename = os.path.join(save_folder, f'image{final_index}.png')
                cv2.imwrite(filename, image)
                
                
    
    print(f'er:{error_message}') # error message to see if manual stitching is required
    sys.stdout.flush()
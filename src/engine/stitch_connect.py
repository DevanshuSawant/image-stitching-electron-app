import cv2
import os
import glob
import sys
import shutil
import time
import matplotlib.pyplot as plt
import numpy as np
import custom_stitch as cust


def delete_images(folder_path):
    image_extensions = [
        "*.jpg",
        "*.jpeg",
        "*.png",
        "*.gif",
    ]  # Add any other image extensions you want to delete

    # Generate a list of all image files in the folder
    image_files = []
    for extension in image_extensions:
        image_files.extend(glob.glob(os.path.join(folder_path, extension)))

    # Delete each image file
    for image_file in image_files:
        os.remove(image_file)
        # print(f"Deleted {image_file}")


def copy_files(source_folder, destination_folder):
    # Get the list of files in the source folder
    files = os.listdir(source_folder)

    # Iterate over the files
    for file_name in files:
        # Construct the full file paths
        source_path = os.path.join(source_folder, file_name)
        destination_path = os.path.join(destination_folder, file_name)

        # Copy the file
        shutil.copy2(source_path, destination_path)

        # Get the file's modification timestamp
        timestamp = os.path.getmtime(source_path)

        # Convert the timestamp to a readable format
        timestamp_str = time.strftime("%Y%m%d%H%M%S", time.localtime(timestamp))

        # Create the new file name by appending the timestamp
        new_file_name = f"{timestamp_str}_{file_name}"

        # Construct the full destination path with the new file name
        new_destination_path = os.path.join(destination_folder, new_file_name)

        # Rename the file
        os.rename(destination_path, new_destination_path)
        print(f"Copied {file_name} to {new_destination_path}")


save_folder = "result-images"
# directory = os.path.dirname(os.path.abspath(save_folder))
# final_directory = os.path.join(directory,save_folder)
# print(final_directory)
# sys.stdout.flush()


def getStitchResult(filenames):
    save_folder2 = "image1.png"
    save_folder1 = "result-images\image1.png"

    directory = os.path.dirname(os.path.abspath(save_folder1))
    final_directory1 = os.path.join(directory, save_folder2)
    print(
        f"finished:{final_directory1}"
    )  # final directory where the result image will be stored
    sys.stdout.flush()

    save_folder = "result-images"
    directory = os.path.dirname(os.path.abspath(save_folder))
    final_directory = os.path.join(directory, save_folder)
    # final_directory_modified = final_directory.replace("\\", "")
    print(
        f"fd:{final_directory}"
    )  # final directory where the result image will be stored
    sys.stdout.flush()
    error_message = 0
    # PATH = 'assets/SMT-scratch/original/'

    feature_extractor = "sift"

    imageBucket = []
    resultImageBucket = []
    previousRunBucket = []
    altImageBucket = []
    number_of_images = len(filenames)
    current_number_of_completed_images = 0
    print(f"tn:{number_of_images}")  # total no of images sent to js file
    sys.stdout.flush()

    for file in filenames:
        imageBucket.append(cv2.imread(file))
        # print(file)
        sys.stdout.flush()

    while True:
        if len(imageBucket) < 2:
            current_number_of_completed_images += 1
            print(
                f"cd:{current_number_of_completed_images}"
            )  # current number of images currently processed if no of images are less than 2
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
            kpsA, featuresA = cust.detectAndDescribe(
                image2_gray, "left", widthSize, method=feature_extractor
            )
            kpsB, featuresB = cust.detectAndDescribe(
                image1_gray, "right", widthSize, method=feature_extractor
            )

            # fig, (ax1,ax2) = plt.subplots(nrows=1, ncols=2, figsize=(20,8), constrained_layout=False)
            # ax1.imshow(cv2.drawKeypoints(image2_gray,kpsA,None,color=(0,255,0)))
            # ax1.set_xlabel("(a)", fontsize=14)

            # ax2.imshow(cv2.drawKeypoints(image1_gray,kpsB,None,color=(0,255,0)))
            # ax2.set_xlabel("(b)", fontsize=14)

            # plt.show()

            # fig = plt.figure(figsize=(20,8))

            matches = cust.matchKeyPointsKNN(
                featuresA, featuresB, ratio=0.73, method=feature_extractor
            )

            # img3 = cv2.drawMatches(image2,kpsA,image1,kpsB,matches,
            #                None,flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

            # plt.imshow(img3)
            # plt.show()
            current_number_of_completed_images += 1
            M = cust.getHomography(
                kpsA, kpsB, featuresA, featuresB, matches, reprojThresh=4
            )
            if M is None:
                # print("Error!")
                # print('Storing in Buffer')
                error_message = 1
                if len(previousRunBucket) > 0:
                    image1 = altImageBucket.pop(0)
                    print(
                        "Couldnt stitch the images so cleared the buffer and did blending for previous stitched image"
                    )

                resultImageBucket.append(image1)
                imageBucket.insert(0, image2)
                previousRunBucket = []
                altImageBucket = []
                print(
                    f"cd:{current_number_of_completed_images}"
                )  # current number of images currently processed if error occurs
                sys.stdout.flush()
                continue

            (matches, H, status) = M

            width = image2.shape[1] + image1.shape[1]
            height = max(image2.shape[0], image1.shape[0])

            result = cv2.warpPerspective(image2, H, (width - 100, height))
            # Calculate the four corners of image2 in the resulting image
            corners = np.array(
                [
                    [0, 0, 1],
                    [0, image2.shape[0], 1],
                    [image2.shape[1], image2.shape[0], 1],
                    [image2.shape[1], 0, 1],
                ]
            )
            transformed_corners = np.dot(H, corners.T)
            transformed_corners /= transformed_corners[
                2
            ]  # Homogeneous coordinates normalization

            # Extract the x and y coordinates of the transformed corners
            x_coords = transformed_corners[0]
            y_coords = transformed_corners[1]

            # Determine the minimum and maximum x and y coordinates to get the bounding box of image2
            min_x = np.min(x_coords)
            min_y = np.min(y_coords)

            overlap_start = (int(min_y), int(min_x), 3)

            # Insert the croppped image to the result image to get rid of the black background
            cropped_image = image1[:, : overlap_start[1] + 16, :]
            result[
                0 : image1.shape[0], 0 : overlap_start[1] + 16
            ] = cropped_image  # left image1 is below image2
            # plt.figure(figsize=(20,10))
            # plt.imshow(result)
            # plt.show()

            # Perform alpha blending
            alpha = 0.5  # Adjust the alpha value as desired
            gamma = 13  # Adjust the gamma value as desired
            blended_region = cv2.addWeighted(
                result[0 : image1.shape[0], 0 : image1.shape[1]],
                alpha,
                image1,
                1 - alpha,
                gamma,
            )
            # result = cv2.addWeighted(result, 1, result, 0, gamma)
            # Replace the blended region in the result
            result[
                0 : blended_region.shape[0], 0 : blended_region.shape[1]
            ] = blended_region
            # previousResultBucket.insert(0, result)
            if len(previousRunBucket) > 0:
                image = previousRunBucket.pop(0)
                if len(imageBucket) == 0:
                    image = cv2.addWeighted(
                        result[0 : image.shape[0], 0 : image.shape[1]],
                        alpha,
                        image,
                        1 - alpha,
                        gamma,
                    )
                else:
                    alt_image = cv2.addWeighted(
                        result[0 : image.shape[0], 0 : image.shape[1]],
                        alpha,
                        image,
                        1 - alpha,
                        gamma,
                    )
                    alt_result = result
                    alt_result[0 : image.shape[0], 0 : image.shape[1]] = alt_image
                    alt_result = cust.removeBlackBg(alt_result)
                    altImageBucket.insert(0, alt_result)
                print(result.shape)
                # plt.figure(figsize=(20,10))
                # plt.imshow(result)
                # plt.show()

                result[0 : image.shape[0], 0 : image.shape[1]] = image
                # print("length of previous run bucket", len(previousRunBucket))

            result = cust.removeBlackBg(result)

            # print("length of image bucket", len(imageBucket))
            # print("length of result image bucket", len(resultImageBucket))
            print(
                f"cd:{current_number_of_completed_images}"
            )  # current number of images currently processed if no error occurs and merged successfully
            sys.stdout.flush()
            previousRunBucket.insert(0, result)
            imageBucket.insert(0, result)

    # Create the directory
    os.makedirs(final_directory, exist_ok=True)

    history_folder = "result-images-history"
    history_directory = os.path.dirname(os.path.abspath(history_folder))
    final_history_directory = os.path.join(history_directory, history_folder)
    os.makedirs(final_history_directory, exist_ok=True)
    copy_files(final_directory, final_history_directory)

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
                filename = os.path.join(save_folder, f"image{index}.png")
                # image = cv2.addWeighted(image, 0.5, image, 0.5, 15)
                cv2.imwrite(filename, image)
                final_index = index
            elif i == 1:
                final_index += index + 1
                filename = os.path.join(save_folder, f"image{final_index}.png")
                # image = cv2.addWeighted(image, 0.5, image, 0.5, 15)
                cv2.imwrite(filename, image)

    print(f"er:{error_message}")  # error message to see if manual stitching is required
    sys.stdout.flush()

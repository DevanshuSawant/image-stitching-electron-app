import cv2
import os
import glob
import sys
import shutil
import time
import imutils
# import matplotlib.pyplot as plt
import numpy as np
# import custom_stitch as cust


def remove_background(stitched):
    print("[INFO] cropping...")
    stitched = cv2.copyMakeBorder(stitched, 10, 10, 10, 10, cv2.BORDER_CONSTANT, (0, 0, 0))
    # convert the stitched image to grayscale and threshold it
    # such that all pixels greater than zero are set to 255
    # (foreground) while all others remain 0 (background)
    gray = cv2.cvtColor(stitched, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)[1]
    
    # find all external contours in the threshold image then find
    # the *largest* contour which will be the contour/outline of
    # the stitched image
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    c = max(cnts, key=cv2.contourArea)
    # allocate memory for the mask which will contain the
    # rectangular bounding box of the stitched image region
    mask = np.zeros(thresh.shape, dtype="uint8")
    (x, y, w, h) = cv2.boundingRect(c)
    cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)
    
    # create two copies of the mask: one to serve as our actual
    # minimum rectangular region and another to serve as a counter
    # for how many pixels need to be removed to form the minimum
    # rectangular region
    minRect = mask.copy()
    sub = mask.copy()
    # keep looping until there are no non-zero pixels left in the
    # subtracted image
    while cv2.countNonZero(sub) > 0:
        # erode the minimum rectangular mask and then subtract
        # the thresholded image from the minimum rectangular mask
        # so we can count if there are any non-zero pixels left
        minRect = cv2.erode(minRect, None)
        sub = cv2.subtract(minRect, thresh)
        
    # find contours in the minimum rectangular mask and then
    # extract the bounding box (x, y)-coordinates
    cnts = cv2.findContours(minRect.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    c = max(cnts, key=cv2.contourArea)
    (x, y, w, h) = cv2.boundingRect(c)
    # use the bounding box coordinates to extract the our final
    # stitched image
    stitched = stitched[y:y + h, x:x + w]
    
    return stitched

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
    stitchy = cv2.Stitcher.create()  # Use createStitcher instead of cv2.Stitcher.create()

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



    imageBucket = []
    resultImageBucket = []

    number_of_images = len(filenames)
    current_number_of_completed_images = 0
    print(f"tn:{number_of_images}")  # total no of images sent to js file
    sys.stdout.flush()

    for file in filenames:
        imageBucket.append(cv2.imread(file))
        print(file)
        sys.stdout.flush()
    print(len(imageBucket))
    for i in range(number_of_images):
        print(i)
        if len(imageBucket) < 2:
            current_number_of_completed_images += 1
            image = imageBucket.pop(0)
            image = remove_background(image)

            imageBucket.insert(0, image)
            print(
                f"cd:{current_number_of_completed_images}"
            )  # current number of images currently processed if no of images are less than 2
            sys.stdout.flush()

            break
        else:
            print("More than 2 images")
            image1 = imageBucket.pop(0)
            image2 = imageBucket.pop(0)
            

            status, output = stitchy.stitch([image1, image2])
            current_number_of_completed_images += 1
            print(f"Stitching...{status}")
            if status != 0:
                print(f"Error:{status}")
                # print('Storing in Buffer')
                error_message = 1
                print("Couldnt stitch the images so cleared the buffer")
                image1 = remove_background(image1)
                resultImageBucket.append(image1)
                imageBucket.insert(0, image2)
                print(f"cd:{current_number_of_completed_images}")  # current number of images currently processed if error occurs
                sys.stdout.flush()
                continue

            result = output

            print("length of image bucket", len(imageBucket))
            print("length of result image bucket", len(resultImageBucket))
            print(
                f"cd:{current_number_of_completed_images}"
            )  # current number of images currently processed if no error occurs and merged successfully
            sys.stdout.flush()
            imageBucket.insert(0, result)

    # Create the directory

    history_folder = "result-images-history"
    history_directory = os.path.dirname(os.path.abspath(history_folder))
    final_history_directory = os.path.join(history_directory, history_folder)

    # desired_height = int(min_height*0.9)
    # imageBucket[0] = crop_image_to_height(imageBucket[0], desired_height)
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
                cv2.imwrite(filename, image)
                final_index = index
            elif i == 1:
                final_index += index + 1
                filename = os.path.join(save_folder, f"image{final_index}.png")
                cv2.imwrite(filename, image)
                
    os.makedirs(final_history_directory, exist_ok=True)
    if os.path.exists(final_directory):
        print("Copying files to history folder")
        copy_files(final_directory, final_history_directory)
    else:
        os.makedirs(final_directory, exist_ok=True)
        
    print(f"er:{error_message}")  # error message to see if manual stitching is required
    sys.stdout.flush()

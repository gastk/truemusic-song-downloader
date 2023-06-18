from PIL import Image
import os
import datetime
import configparser

def pause():
    input("Press <ENTER> key to continue...")

# This logs errors to the errors file
def log_error(screen_message, log_details, exception = None):
    try:
        now = datetime.datetime.now()
        formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")

        with open(errorsFile, "a") as file:
            file.write(f"[{formatted_datetime}]\nMessage: {screen_message}\nDetails: {log_details}\nException: {str(exception)}\n------------\n\n")
        
        print(f"---- /!\\ {screen_message}\nException details: {exception}\n\n")
        return
    except Exception as e:
        print(f"!!!!!--- Critical error ocurred while trying to save an error!\nException: {e}\n\n")
        print(f"!!-- Original error details that we tried to save but failed:\nMessage: {screen_message}\nDetails: {log_details}\nException: {exception}")
        pause()

try:
    # Read the config.ini file
    config = configparser.ConfigParser()
    config.read('config.ini')

    ### Read and define the settings
    outputPath = config.get("Download", "output_path").strip()
    errorsFile = config.get("MandatoryFiles", "errors_filename").strip()

    #region Initial validations

    if errorsFile == "":
        print(f"---- /!\\ The config \"errors_filename\" is not defined in \"config.ini\" file! You must define it.\n")
        pause()
        exit()

    if outputPath == "":
        log_error(f"The config \"output_path\" is not defined in \"config.ini\" file! You must define it.", None)
        pause()
        exit()
    
    if errorsFile == outputPath:
        log_error(f"The settings \"output_path\" and \"errors_filename\" must be different in \"config.ini\".", None)
        pause()
        exit()

    if os.path.isdir(outputPath) == False:
        log_error(f"The output path \"outputPath\" does not exist! You must create it.", None)
        pause()
        exit()
    
    if os.path.isfile(errorsFile) == False:
        log_error(f"The errors log file \"{errorsFile}\" does not exist! You must create it.", None)
        pause()
        exit()

    #endregion Initial validations

except Exception as e:
    print(f"/!\\ ERROR: Unknown error ocurred while parsing CONFIG file! Maybe the file doesn't exists?\nUnable to continue.\n")
    print(f"Exception details:\n{e}\n")
    pause()
    exit()

# Filenames that should be ignored (System files, for example)
ignore_list = ["AlbumArtSmall.jpg", "Folder.jpg"]

def crop_4_3_aspect_ratio(image):
    width, height = image.size
    target_ratio = 4 / 3
    current_ratio = width / height
    if current_ratio > target_ratio:
        # Image width is larger, so we cut it.
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        right = width - new_width - left
        image = image.crop((left, 0, width - right, height))
    else:
        # Image height is larger, so we cut it.
        new_height = int(width / target_ratio)
        top = (height - new_height) // 2
        bottom = height - new_height - top
        image = image.crop((0, top, width, height - bottom))
    return image

def crop_square_aspect_ratio(image):
    width, height = image.size
    target_size = min(width, height)
    left = (width - target_size) // 2
    top = (height - target_size) // 2
    right = left + target_size
    bottom = top + target_size
    image = image.crop((left, top, right, bottom))
    return image

#region Backup disabled
# # Creates a backup of the folder
# backup_dir_name = "Backups\\backup_crop_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
# backup_dir_path = os.path.join(os.path.dirname(outputPath), backup_dir_name)
# os.makedirs(backup_dir_path)

# # Copy all the files from source to backup
# for filename in os.listdir(outputPath):
#     file_path = os.path.join(outputPath, filename)
#     if os.path.isfile(file_path):
#         if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"):
#             shutil.copy2(file_path, backup_dir_path)
#endregion Backup disabled

# Check all images from the folder to see if they are square
for filename in os.listdir(outputPath):
    if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"):
        
        print(f"\n----- FILE START: {filename}")
        # Ignores the current file if they are in the ignore list
        if filename in ignore_list:
            continue
        
        # Get the image width and height
        image_path = os.path.join(outputPath, filename)
        img = Image.open(image_path)
        width, height = img.size
        
        # Checks if the image is already a square
        if width == height:
            continue
        
        # As it's not a square, this will turn it into one
        img = crop_square_aspect_ratio(img)
        
        new_image_path = os.path.join(outputPath, filename)
        img.save(new_image_path)
        print(f"----- CROPPED: {filename}")

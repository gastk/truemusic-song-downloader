import configparser
import os
import datetime
import yt_dlp
import re
import sys
from unidecode import unidecode
from urllib.parse import urlparse, parse_qs

def pause():
    input("Press <ENTER> key to continue...")

# This logs errors to the errors file
def log_error(screen_message, log_details, exception = None):
    try:
        now = datetime.datetime.now()
        formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")

        with open(errorsFile, "a", encoding="utf-8") as file:
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
    downloadThumbs = config.getboolean("Download", "download_thumbnails")
    addReleaseYear = config.getboolean("Download", "add_release_year")
    audioQuality = config.get("Download", "audio_quality").strip()
    ampersandReplace = config.get("Download", "ampersand_replace").strip()
    errorsFile = config.get("MandatoryFiles", "errors_filename").strip()
    downloadsFile = config.get("MandatoryFiles", "already_downloaded_filename").strip()

    #region Initial validations

    #region Mandatory settings (They will stop the script)
    if errorsFile == "":
        print(f"---- /!\\ The config \"errors_filename\" is not defined in \"config.ini\" file! You must define it.\n")
        pause()
        exit()

    if outputPath == "":
        log_error(f"The config \"output_path\" is not defined in \"config.ini\" file! You must define it.", None)
        pause()
        exit()

    if downloadsFile == "":
        log_error(f"The config \"already_downloaded_filename\" is not defined in \"config.ini\" file! You must define it.", None)
        pause()
        exit()
    
    if errorsFile == outputPath or errorsFile == downloadsFile or outputPath == downloadsFile:
        log_error(f"One of following settings are duplicated: \"output_path\" or \"errors_filename\" or \"already_downloaded_filename\"! They must be different.", None)
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
    
    if os.path.isfile(downloadsFile) == False:
        log_error(f"The downloads log file \"{downloadsFile}\" does not exist! You must create it.", None)
        pause()
        exit()
    #endregion Mandatory settings (They will stop the script)
    
    #region Apply default settings if empty
    if audioQuality == "":
        audioQuality = "128K"
    
    if ampersandReplace == "":
        ampersandReplace = "and"
    
    #endregion Apply default settings if empty

    #endregion Initial validations

except Exception as e:
    print(f"/!\\ ERROR: Unknown error ocurred while parsing CONFIG file! Maybe the file doesn't exists?\nUnable to continue.\n")
    print(f"Exception details:\n{e}\n")
    pause()
    exit()

# Options JSON for YT-DLP
options = {
    "format": "bestaudio",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "vorbis",
            "preferredquality": "128K",
        },
        {
            "format": "jpg",
            "key": "FFmpegThumbnailsConvertor",
            "when": "before_dl",
        }
    ],
    "writethumbnail": downloadThumbs,
    "fixup": "detect_or_warn",
}

def sanitize_text(text):
    # Remove accents and convert to ASCII characters
    return unidecode(text)

def sanitize_file_name(file_name):
    try:
        # Replace some invalid characters (for Windows) with underscore
        invalid_chars = r'[\\/:*?"<>|]'
        file_name = re.sub(invalid_chars, '_', file_name)
        
        # Replace "&" with the defined character (config.ini)
        file_name = file_name.replace('&', ampersandReplace)

        file_name = sanitize_text(file_name)

    except Exception as e:
        now = datetime.datetime.now()
        formatted_datetime = now.strftime("%Y_%m_%d %H_%M_%S")
        message = f"Unhandled error while parsing YouTube URL: {url}"
        log_error(message, url, e)
        file_name = f"error_{formatted_datetime}"

    return file_name

# This is here so it gets the
def get_video_id_from_url(url):
    try:
        parsed_url = urlparse(url)
        if parsed_url.netloc == 'youtu.be':
            video_id = parsed_url.path[1:]
            video_id = video_id.split('?')[0]
        elif parsed_url.netloc == 'www.youtube.com' and parsed_url.path == '/watch':
            query_params = parse_qs(parsed_url.query)
            video_id = query_params.get('v', [None])[0]
        else:
            video_id = None
        return video_id
    except Exception as e:
        message = f"An error ocurred while parsing the URL: {url}"
        log_error(message, url, e)
        video_id = None
    
    return video_id

def download_audio(url):
    ydl = yt_dlp.YoutubeDL(options)
    
    # Parse the URL and check if it's from YouTube
    video_id = get_video_id_from_url(url)
    
    if not video_id:
        print(f"---- URL is not a valid YouTube URL: {url}")
        return False
    
    url = f"https://youtu.be/{video_id}"

    # Check if the video has already been downloaded by it's ID
    with open(downloadsFile, "r", encoding="utf-8") as file:
        if f"ID:{video_id}" in file.read():
            print(f"---- The video '{video_id}' has already been downloaded.")
            return False

    try:
        info = ydl.extract_info(url, download=False)
    except Exception as e:
        message = f"Exception ocurred while extracting URL: {url}"
        log_error(message, url, e)
        return
    
    artist = info.get("artist")
    track = info.get("track")
    release_year = info.get("release_year") if addReleaseYear else None
    title = info.get("title")
    
    # Defines if the downloaded video is from YouTube Music or is an ordinary video
    not_ytmusic_video = False
    log_song_name = None

    if release_year and artist and track:
        file_name = f"{artist[:70]} - {track[:70]} ({release_year})"
        log_song_name = f"{artist[:70]}_{track[:70]}"
    elif artist and track:
        file_name = f"{artist[:70]} - {track[:70]}"
        log_song_name = f"{artist[:70]}_{track[:70]}"
    elif title:
        file_name = f"edit_{title[:170]}"
        not_ytmusic_video = True
    else:
        file_name = "unknown_" + datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        not_ytmusic_video = True

    # Check if the track has already been downloaded by it's name
    if not_ytmusic_video == False and log_song_name is not None:
        with open(downloadsFile, "r", encoding="utf-8") as file:
            if f"Songname:{log_song_name}" in file.read():
                print(f"---- The track '{artist[:70]} - {track[:70]}' has already been downloaded.")
                return False

    file_name = sanitize_file_name(file_name)
    file_path = os.path.join(outputPath, file_name)
    
    ydl_opts = options.copy()
    ydl_opts["outtmpl"] = file_path
    if not_ytmusic_video:
        ydl_opts["writethumbnail"] = False
    ydl = yt_dlp.YoutubeDL(ydl_opts)
    
    try:
        ydl.download([url])
    except Exception as e:
        message = f"Exception ocurred while downloading ID: {video_id}"
        log_error(message, url, e)
        return False
    
    now = datetime.datetime.now()
    formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
    
    with open(downloadsFile, "a", encoding="utf-8") as file:
        if not_ytmusic_video or log_song_name is None:
            file.write(f"[{formatted_datetime}]\nID:{video_id}\n\n")
        else:
            file.write(f"[{formatted_datetime}]\nID:{video_id}\nSongname:{log_song_name}\n\n")
    
    return True

os.system('cls')
# If an URL is passed as parameter when opening the script, do:
if len(sys.argv) > 1:
    url = sys.argv[1]
    os.system('cls')

    # Download the video from that URL
    try:
        ret = download_audio(url)
    except Exception as e:
        message = f"!!! Unhandled Exception ocurred: {url}"
        log_error(message, url, e)

    if ret == True:
        print(f"\n----- {url} downloaded!")
    else:
        print(f"\n----- Something happened!")
else:
    while True:
        print("\n\n-----------------")
        print("True Music mod songs downloader")
        print("Download your songs from YouTube and convert them easily for the Project Zomboid mod you love\n")
        print("Tip: Any video works, but it's better to download official ones. Playlists are currently NOT supported.")
        print("-----------------\n")

        url = input("Enter the URL to download:\n")
        os.system('cls')
        
        try:
            ret = download_audio(url)
        except Exception as e:
            message = f"!!! Unhandled Exception ocurred when trying to download the URL:\n{url}\n\nUnable to continue, the app will close."
            log_error(message, url, e)
            pause()
            exit()

        if ret == True:
            print(f"\n----- {url} downloaded!")
        else:
            print(f"\n----- Something happened!")
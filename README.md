# Song Downloader for True Music
A python script I created to make creating a new True Music mod even easier than before!

[True Music](https://steamcommunity.com/workshop/filedetails/?id=2613146550) is a mod that adds real life songs in [Project Zomboid](https://store.steampowered.com/app/108600/Project_Zomboid/), an open-ended zombie-infested sandbox game. 

## But it's so easy to create an addons, why you made this?
Because I wanted to make an addon for this mod (there are not enough Brazilian song addons for this mod, sadly), and I was too lazy to waste about 5 hours downloading the songs I wanted and editing the names manually.

So, like any good programmer, I preferred to waste days creating and debugging this instead lmao. But it works and I'm happy with it!

## Functionalities

- This script will download any video from YouTube and convert it to .ogg
- If you download the songs from official channels (the "topic" ones), it will almost-automagically rename the file to the standard True Music format.
- It also downloads the thumbnails for these official videos.

## Requirements
I created and tested on:
- Windows (may or may not work on Linux, I never tested it)
- Python 3.10.3
- Module Pillow 9.0.1
- Module Unidecode 1.3.6
- Module yt-dlp 2023.3.4

You can install these modules with:
```
pip install -r requirements.txt
```

## Usage

1. Before starting, check the "config.ini" for any changes that you want to make.
2. Then just open "song_downloader.py" and paste the YouTube video URL you want to download.
3. OPTIONAL if not downloading thumbnails: After downloading all songs, run "crop_images_to_square.py" to crop all the thumbnails you just downloaded.
4. Check the songs you downloaded for any file that starts with "edit_" or "unknown_"
5. All done, now just copy and paste the songs to your True Music addon folder. 
- If you don't know how to do this, refer to the [mod page on Steam Workshop](https://steamcommunity.com/workshop/filedetails/?id=2613146550) to download the template and know where to put these files.

## License

[True Music](https://steamcommunity.com/workshop/filedetails/?id=2613146550) original mod or True Music template addon was not made by me, but by this [fine gentleman](https://www.patreon.com/_tsar).

The script on this page was made by me. You can do whatever you want with it, just don't kill the universe.

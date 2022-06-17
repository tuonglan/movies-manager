import requests, io, os, shutil, cloudscraper
import zipfile, rarfile

SUPPORTED_EXT=['srt', 'ass']

def _create_request(link):
    print("Downloading %s" % link)
    req = requests.get(link)
    
    # Disable Proxy if needed method 1
    if req.status_code != 200:
        print("\tUsing proxy method1...")
        req = requests.get(link, proxies={'http': None, 'https': None})
    if req.status_code != 200:
        print("\tUsing proxy method2...")
        ses = requests.Session()
        ses.trust_env = False
        req = ses.get(link)

    if req.status_code != 200:
        print("\tUsing cloudscraper library...")
        while True:
            scraper = cloudscraper.create_scraper()
            req = scraper.get(link)
            if req.status_code == 200:
                break
            else:
                text = input("\t\tFailed to scrape the subtitles, press Enter ONLY to try again, other to exit:")
                if text != '':
                    break

    if req.status_code != 200:
        raise Exception("Can't download !! Code %s, msg: %s" % (req.status_code, req.text))

    return req

def _get_sub_filename(files):
    ass_file = None
    for f in files:
        if f.lower().endswith('.srt'):
            return f
        if f.lower().endswith('.ass'):
            ass_file = f

    if ass_file:
        return ass_file
    else:
        raise Exception("Empty zipped sub file")

def download_sub_to_file(link, video_file, lang):
    # Download the file
    req = _create_request(link)

    # Extract the file as zip
    try:
        stream = io.BytesIO(req.content)
        with zipfile.ZipFile(stream) as zipper:
            sub_filename = _get_sub_filename(zipper.namelist())
            sub_file = "%s.%s.%s" % (video_file.rsplit('.', 1)[0], lang, sub_filename.rsplit('.', 1)[1])
            print("Extracting %s to %s" % (sub_filename, os.path.basename(sub_file)))
            with open(sub_file, 'wb') as sin:
                with zipper.open(sub_filename) as sout:
                    sin.write(sout.read())
    # Extract the file as rar
    except zipfile.BadZipFile:
        print("Not *.zip file, trying with RAR")
        stream = io.BytesIO(req.content)
        with rarfile.RarFile(stream) as zipper:
            sub_filename = _get_sub_filename(zipper.namelist())
            sub_file = "%s.%s.%s" % (video_file.rsplit('.', 1)[0], lang, sub_filename.rsplit('.', 1)[1])
            print("Extracting %s to %s" % (sub_filename, os.path.basename(sub_file)))
            with open(sub_file, 'wb') as sin:
                with zipper.open(sub_filename) as sout:
                    sin.write(sout.read())


def exits(video_file, lang_3):
    basename = "%s.%s" % (os.path.splitext(video_file)[0], lang_3)
    for ext in SUPPORTED_EXT:
        name = "%s.%s" % (basename, ext)
        if os.path.isfile(name):
            return True

    return False

def copy(sub_file, video_file, lang_3):
    target_sub_file = "%s.%s%s" % (os.path.splitext(video_file)[0], lang_3, os.path.splitext(sub_file)[1])
    if sub_file != target_sub_file:
        shutil.copy(sub_file, target_sub_file)
    else:
        print ("WARNING: Source %s is identical to des %s" % (sub_file, target_sub_file))



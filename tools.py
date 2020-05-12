import os, glob, re


PTT_DIR1 = re.compile('(.+?) \(((?:19|20)\d\d)\)(.*)')
PTT_DIR2 = re.compile('(.+?)\.((?:19|20)\d\d)(.*)')
PTT_FILE = re.compile('(.+?)((?:19|20)\d\d)(.*)')
PTT_TEAM = re.compile('.*- ?(.+?)\..*')

# Codec matcher
H264 = re.compile('x264|h264')
H265 = re.compile('x265|h265|hevc')
XVID = re.compile('xvid')
DIVX = re.compile('divx')

# Resolution matcher
HD = re.compile('720p|720|hd')
FHD = re.compile('1080p|1080|fullhd|full\.hd|fhd')
UHD = re.compile('2160p|uhd|4k')

# Source matcher
BLUERAY = re.compile('blu-ray|bluray|bdrip|brip|brrip|bdr')
WEBRIP = re.compile('web-dl|webrip|web-rip|webdl')
DVDRIP = re.compile('dvdrip|dvd-rip|dvd rip')

# Language matcher
ENGLISH = re.compile('eng.srt|eng.ass|\(eng\)|\(english\)')
VIETNAMESE = re.compile('vie.srt|vie.ass|\(vie\)|\(vietnamese\)')

# Team matcher
YIFY = re.compile('yify|yts')
RARBG = re.compile('rarbg')
SPARKS = re.compile('sparks')
GECKOS = re.compile('geckos')
MKVCAGE = re.compile('mkvcage')
ANOXMOUS = re.compile('anoxmous')
AXXO = re.compile('axxo')


def get_movie_info_from_dir(dir_name):
    m = PTT_DIR1.match(dir_name)
    if m:
        return m

    m = PTT_DIR2.match(dir_name)
    return m

def get_movie_info_from_file(file_name):
    return PTT_FILE(file_name)

def scan_subtitles_info(video_file):
    sub_info = {}
    base = os.path.splitext(video_file)[0]
    files = glob.glob("%s*" % glob.escape(base))
    for f in files:
        postfix = f[len(base):].lower()     # Take the postfix of the file only
        if ENGLISH.search(postfix) or postfix == '.srt' or postfix == '.ass':
            sub_info['English'] = f
        elif VIETNAMESE.search(postfix):
            sub_info['Vietnamese'] = f
        else:
            pass

    return sub_info

def get_codec(name, file):
    if H265.search(name):
        codec = 'H265'
    elif H264.search(name):
        codec = 'H264'
    elif XVID.search(name):
        codec = 'XVID'
    elif DIVX.search(name):
        codec = 'DIVX'
    else:
        # TODO: Use ffmpeg to get codec, implement later
        codec = 'unk_codec'
    
    return codec

def get_resolution(name, file):
    if UHD.search(name):
        resolution = '2160p'
    elif FHD.search(name):
        resolution = '1080p'
    elif HD.search(name):
        resolution = '720p'
    else:
        # TODO: Use ffmpeg to get the resolution, implement later
        resolution = 'unk_resolution'
    
    return resolution

def get_source(name, file):
    if BLUERAY.search(name) and not WEBRIP.search(name):
        source = 'Bluray'
    elif WEBRIP.search(name):
        source = 'WebRip'
    elif DVDRIP.search(name):
        source = 'DVDRip'
    else:
        source = 'unk_source'
    
    return source

def get_team(name, file):
    if YIFY.search(name):
        team = 'YIFY'
    elif RARBG.search(name):
        team = 'RARBG'
    elif SPARKS.search(name):
        team = 'SPARKS'
    elif GECKOS.search(name):
        team = 'GECKOS'
    elif MKVCAGE.search(name):
        team = 'MkvCage'
    elif ANOXMOUS.search(name):
        team = 'anoXmous'
    elif AXXO.search(name):
        team = 'aXXo'
    else:
        m = PTT_FILE.match(name)
        if m and m.group(3):
            t = PTT_TEAM.match(m.group(3))
            if t and t.group(1):
                team = t.group(1).upper()
            else:
                team = 'unk_team'
        else:
            team = 'unk_team'
        #print("==============> %s: %s" % (name, team))

    return team



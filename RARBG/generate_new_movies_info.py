import os, glob, re, json
from pprint import pprint


PTT = re.compile('(.+?)\.((?:19|20)\d\d)\.(.+)')

def scan_new_movies_dir(path):
    movies_db = {}
    for mov_path in glob.glob(os.path.join(glob.escape(path), '*')):
        print("Scanniing %s" % mov_path)
        video_files = glob.glob(os.path.join(glob.escape(mov_path), '*.mp4'))
        if not video_files:
            video_files = glob.glob(os.path.join(glob.escape(mov_path), '*.mkv'))
        if not video_files:
            print("\tERROR: Can't find any video in %s" % os.path.basename(mov_path))
            movies_db.setdefault('error', {})[mov_path] = []
            continue

        gen = (f for f in video_files)
        try:
            while True:
                video_filename = os.path.basename(next(gen)).lower()
                m = PTT.match(video_filename)
                if not m:
                    print("\tWARNING: Invalid file name: %s" % video_filename)
                    movies_db.setdefault('error', {}).setdefault(mov_path, []).append(video_filename)
                    continue

                name = m.group(1)
                year = m.group(2)
                resolution = '2160p' if '2160p' in m.group(3) else '1080p' if '1080p' in m.group(3) else '720p'
                codec = 'H265' if 'x265' in m.group(3) else 'H264'
                mov_name = "%s.%s" % (name, year)
                quality = "%s.%s" % (resolution, codec)
                info = movies_db.setdefault(mov_name, {'current': None, 'new': {}})
                info['new'][quality] = mov_path
                break
        except StopIteration:
            print("\tERROR: None valid video file found")
            continue
            
    return movies_db

def generate_new_movies_db(path):
    movies_db = {}
    for d in glob.glob(os.path.join(path, '*')):
        print("-----> Scanning %s" % d)
        dir_name = os.path.basename(d).lower()
        m = PTT.match(dir_name)
        name = m.group(1).lower()
        quality = '2160p' if '2160p' in m.group(3) else '1080p'
        codec = 'x265' if 'x265' in m.group(3) else 'h264'
        sub_key = "%s_%s" % (quality, codec)
        value = movies_db.setdefault("%s.%s" % (name, m.group(2)), {'current': None, 'new': {}})
        value['new'][sub_key] = d

    return movies_db

def generate_new_movies_db_yts(path):
    movies_db = {}
    for d in glob.glob(os.path.join(path, '*')):
        print("------> Scanning %s..." % d)
        dir_name = os.path.basename(d).lower()
        m = PTT_YTS.match(dir_name)
        if not m:
            print("\t Can't scan %s, not YTS movie" % dir_name)
            continue
        name = m.group(1).rstrip().replace(' ', '.')
        quality = '2160p' if '2160' in m.group(3) else '1080p'
        codec = 'x265'
        sub_key = '%s_%s' % (quality, codec)
        value = movies_db.setdefault("%s.%s" % (name, m.group(2)), {'current': None, 'new': {}})
        value['new'][sub_key] = d

    return movies_db

def compare_movies(new_movies, current_movies):
    no_match = []
    for name, value in new_movies['movies_db'].items():
        if current_movies.get(name):
            value['current'] = current_movies[name]
        else:
            no_match.append(name)

    new_movies['no_match'] = no_match


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--path', type=str, help='Directory for scanning')
    parser.add_argument('--current_movies', type=str, default='', help='The current movies file')
    parser.add_argument('--out', type=str, default='', help='Output file')
    args = parser.parse_args()

    movies_db = scan_new_movies_dir(args.path)
    new_movies = {'movies_db': movies_db}

    # Read the current movies
    if args.current_movies:
        with open(args.current_movies) as sin:
            current_movies_db = json.load(sin)
            compare_movies(new_movies, current_movies_db['movies_db']['brief'])

    if args.out:
        with open(args.out, 'w') as fout:
            json.dump(new_movies, fout, indent=4, sort_keys=True)

import os, glob, re, json, shutil
from pprint import pprint


PTT = re.compile('(.+?)\.((?:19|20)\d\d)\.(.+)')
PTT_YTS = re.compile('(.+?)\((\d\d\d\d)\)(.+)')

ROMAN = re.compile('^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$')

def key_to_name(key):
    def cap(w):
        if ROMAN.match(w.upper()):
            return w.upper()
        else:
            return w.capitalize()

    ls = key.split('.')
    name = ' '.join([cap(w) for w in ls[0:-1]])
    return "%s (%s)" % (name, ls[-1])

def move_current_movies(new_path, old_path, movies_db, limit, exe=False):
    data = {'cmds': {}, 'skips': {}}
    idx = 0

    for d in glob.glob(os.path.join(new_path, '*')):
        if limit > 0 and idx >= limit:
            break
        idx += 1

        # Gathering movies information
        dir_name = os.path.basename(d).lower()
        print("\n-------- Processing %s ---------" % dir_name)
        m = PTT.match(dir_name)
        name = m.group(1).lower()
        quality = '2160p' if '2160p' in m.group(3) else '1080p'
        codec = 'x265' if 'x265' in m.group(3) else 'h264'
        key = "%s.%s" % (name, m.group(2))
        sub_key = "%s_%s" % (quality, codec)

        data['cmds'].setdefault(key, {})
        data['cmds'][key][sub_key] = []
        cmd = []
        videos = glob.glob(os.path.join(glob.escape(d), '*.mp4'))
        if not videos:
            videos = glob.glob(os.path.join(glob.escape(d), '*.mkv'))
        if not videos:
            data['skips'].setdefault(key, {})
            data['skips'][key][sub_key] = 'Empty directory'
            next

        mp4_file = videos[0]
        mp4_name = os.path.splitext(os.path.basename(mp4_file))[0]
        srts = glob.glob(os.path.join(glob.escape(d), '*.srt'))
        movie_dir = os.path.join(old_path, key_to_name(key))
        
        if movies_db[key]['current'] and os.path.isdir(movies_db[key]['current']):
            if not os.path.isdir(movie_dir):
                os.mkdir(movie_dir)
            files = glob.glob(os.path.join(glob.escape(movies_db[key]['current']), '*'))
            for f in files:
                data['cmds'][key][sub_key].append("Move: %s -> %s" % (f, movie_dir))
                if exe:
                    shutil.move(f, movie_dir)
        
        # Skipp it
        else:
            data['skips'].setdefault(key, {})
            data['skips'][key][sub_key] = 'Totally new movies'

    return data

def move_new_movies(new_path, movies_db, limit, exe=False, is_yts=False):
    data = {'cmds': {}, 'skips': {}}
    idx = 0

    for d in glob.glob(os.path.join(new_path, '*')):
        if limit > 0 and idx >= limit:
            break
        idx += 1

        # Gathering movies information
        dir_name = os.path.basename(d).lower()
        print("\n-------- Processing %s ---------" % dir_name)
        if is_yts:
            m = PTT_YTS.match(dir_name)
            name = m.group(1).rstrip().replace(' ', '.')
            quality = '2160p' if '2160' in m.group(3) else '1080p'
            codec = 'x265'
        else:
            m = PTT.match(dir_name)
            name = m.group(1).lower()
            quality = '2160p' if '2160p' in m.group(3) else '1080p'
            codec = 'x265' if 'x265' in m.group(3) else 'h264'
        
        key = "%s.%s" % (name, m.group(2))
        sub_key = "%s_%s" % (quality, codec)

        data['cmds'].setdefault(key, {})
        cmd = []
        videos = glob.glob(os.path.join(glob.escape(d), '*.mp4'))
        if not videos:
            videos = glob.glob(os.path.join(glob.escape(d), '*.mkv'))
        if not videos:
            data['skips'].setdefault(key, {})
            data['skips'][key][sub_key] = 'Empty directory'
            next

        mp4_file = videos[0]
        mp4_name = os.path.splitext(os.path.basename(mp4_file))[0]
        srts = glob.glob(os.path.join(glob.escape(d), '*.srt'))
        srts.extend(glob.glob(os.path.join(glob.escape(d), '*.ass')))

        # Start moving files around
        # Move current files to old directory if it is available
        if movies_db[key]['current'] and os.path.isdir(movies_db[key]['current']):
            data['cmds'][key][sub_key] = ["Move: %s -> %s"  % (mp4_file, movies_db[key]['current'])]
            for srt in srts:
                data['cmds'][key][sub_key].append("Move: %s -> %s" % (srt, movies_db[key]['current']))
            if exe:
                shutil.move(mp4_file, movies_db[key]['current'])
                for srt in srts:
                    shutil.move(srt, movies_db[key]['current'])

        # Skipp it
        else:
            data['skips'].setdefault(key, {})
            data['skips'][key][sub_key] = 'Totally new movies'

    return data


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--new_path', type=str, help='Location of the new movies')
    parser.add_argument('--old_path', type=str, help='Location to move the old movies to')
    parser.add_argument('--new_movies_db', type=str, help='Movies DB file')
    parser.add_argument('--out', type=str, default='', help='Output file')
    parser.add_argument('--exe', action='store_true', help='Execute or just show')
    parser.add_argument('--action', type=str, default='', choices=['', 'old', 'new'], help='Select type of action')
    parser.add_argument('--limit', type=int, default=0, help='How many dirs to execute')
    parser.add_argument('--yts', action='store_true', help='Is movie YTS or not')
    args = parser.parse_args()

    with open(args.new_movies_db) as sin:
        movies_db = json.load(sin)
    output = {}

    if args.action == 'old':
        data = move_current_movies(args.new_path, args.old_path, movies_db['movies_db'], args.limit, args.exe)
        output['old'] = data

    if args.action == 'new':
        data = move_new_movies(args.new_path, movies_db['movies_db'], args.limit, args.exe, args.yts)
        output['new'] = data

    if args.out:
        with open(args.out, 'w') as sout:
            json.dump(output, sout, indent=4, sort_keys=True)



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

def move_current_movies(movies_db, path, limit, exe=False):
    data = {'cmds': {}, 'skips': {}}
    idx = 0

    for mov_name, mov_data in movies_db.items():
        for mov_quality, mov_path in mov_data['new'].items():
            if limit > 0 and idx >= limit:
                break
            idx += 1

            movie_dir = os.path.join(path, key_to_name(mov_name))
            
            if movies_db[mov_name]['current'] and os.path.isdir(movies_db[mov_name]['current']):
                if not os.path.isdir(movie_dir) and exe:
                    os.makedirs(movie_dir)
                files = glob.glob(os.path.join(glob.escape(movies_db[mov_name]['current']), '*'))
                data['cmds'].setdefault(mov_name, {}).setdefault(mov_quality, [])
                for f in files:
                    data['cmds'][mov_name][mov_quality].append("Move: %s -> %s" % (f, movie_dir))
                    if exe:
                        shutil.move(f, movie_dir)
            
            # Skipp it
            else:
                data['skips'].setdefault(mov_name, {})[mov_quality] = 'Totally new movies'

    return data

def move_new_movies(movies_db, limit, exe=False):
    data = {'cmds': {}, 'skips': {}}
    idx = 0
    
    for mov_name, mov_data in movies_db.items():
        for mov_quality, mov_path in mov_data['new'].items():
            if limit > 0 and idx >= limit:
                break
            idx += 1

            data['cmds'].setdefault(mov_name, {})
            cmd = []
            videos = glob.glob(os.path.join(glob.escape(mov_path), '*.mp4'))
            if not videos:
                videos = glob.glob(os.path.join(glob.escape(mov_path), '*.mkv'))
            if not videos:
                data['skips'].setdefault(mov_name, {})[mov_quality] = 'Empty directory'
                continue

            mp4_file = videos[0]
            mp4_name = os.path.splitext(os.path.basename(mp4_file))[0]
            srts = glob.glob(os.path.join(glob.escape(mov_path), '*.srt'))
            srts.extend(glob.glob(os.path.join(glob.escape(mov_path), '*.ass')))

            # Start moving files around
            # Move current files to old directory if it is available
            if movies_db[mov_name]['current']:
                data['cmds'][mov_name][mov_quality] = ["Move: %s -> %s"  % (mp4_file, movies_db[mov_name]['current'])]
                for srt in srts:
                    data['cmds'][mov_name][mov_quality].append("Move: %s -> %s" % (srt, movies_db[mov_name]['current']))
                if exe:
                    if not os.path.isdir(movies_db[mov_name]['current']):
                        os.makedirs(movies_db[mov_name]['current'])
                    shutil.move(mp4_file, movies_db[mov_name]['current'])
                    for srt in srts:
                        shutil.move(srt, movies_db[mov_name]['current'])

            # Skipp it
            else:
                data['skips'].setdefault(mov_name, {})[mov_quality] = 'Totally new movies'

    return data


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--move_path', type=str, help='Location to move the old movies to')
    parser.add_argument('--new_movies_db', type=str, help='New Movies DB file')
    parser.add_argument('--out', type=str, default='', help='Output file')
    parser.add_argument('--exe', action='store_true', help='Execute or just show')
    parser.add_argument('--action', type=str, default='', choices=['', 'old', 'new'], help='Select type of action')
    parser.add_argument('--limit', type=int, default=0, help='How many dirs to execute')
    args = parser.parse_args()

    with open(args.new_movies_db) as sin:
        new_movies_db = json.load(sin)
    output = {}

    if args.action == 'old':
        data = move_current_movies(new_movies_db['movies_db'], args.move_path, args.limit, args.exe)
        output['old'] = data

    if args.action == 'new':
        data = move_new_movies(new_movies_db['movies_db'], args.limit, args.exe)
        output['new'] = data

    if args.out:
        with open(args.out, 'w') as sout:
            json.dump(output, sout, indent=4, sort_keys=True)



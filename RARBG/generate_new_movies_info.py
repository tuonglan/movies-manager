import os, glob, re, json
from pprint import pprint


PTT = re.compile('(.+?)\.((?:19|20)\d\d)\.(.+)')
PTT_YTS = re.compile('(.+?)\((\d\d\d\d)\)(.+)')

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
    parser.add_argument('--is_yts', action='store_true', help='Does the movies belong to YTS')
    args = parser.parse_args()

    if args.is_yts:
        movies_db = generate_new_movies_db_yts(args.path)
    else:
        movies_db = generate_new_movies_db(args.path)
    new_movies = {'movies_db': movies_db}

    # Read the current movies
    if args.current_movies:
        with open(args.current_movies) as sin:
            current_movies_db = json.load(sin)
            compare_movies(new_movies, current_movies_db['movies_db']['brief'])

    if args.out:
        with open(args.out, 'w') as fout:
            json.dump(new_movies, fout, indent=4, sort_keys=True)

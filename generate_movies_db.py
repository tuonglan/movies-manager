import os, glob, re, json
from pprint import pprint

import tools as TOOLS


def get_videos_info(videos, current_info={}):
    info = current_info if current_info else {}
    key_idx = 1
    for v in videos:
        name = os.path.basename(v).lower()

        # Get codec
        codec = TOOLS.get_codec(name, v)

        # Get resolution
        resolution = TOOLS.get_resolution(name, v)
        
        # Get source
        source = TOOLS.get_source(name, v)

        # Get team
        team = TOOLS.get_team(name, v)

        # Get subtitles
        subtitles = TOOLS.scan_subtitles_info(v)

        # Set key:
        key = "%s.%s" % (resolution, codec)
        if key in info:
            key = "%s.%s" % (key, team)
            if key in info:
                key = "%s.%s" % (key, key_idx)
                key_idx += 1

        # Set the value
        info[key] = {
            'file': v,
            'source': source,
            'team': team,
            'subtitles': subtitles
        }

    return info

def scan_recursive_file(fulltree, tree, err, stats, path):
    print("----> Scanninng %s" % path)
    videos = glob.glob(os.path.join(glob.escape(path), '*.mp4'))
    videos.extend(glob.glob(os.path.join(glob.escape(path), '*.mkv')))
    videos.extend(glob.glob(os.path.join(glob.escape(path), '*.avi')))
    videos.extend(glob.glob(os.path.join(glob.escape(path), '*.ts')))
    if not videos:
        sub_dirs = [d for d in glob.glob(os.path.join(path, '*')) if os.path.isdir(d)]
        for d in sub_dirs:
            try:
                scan_recursive_file(fulltree, tree, err, stats, d)
            except Exception as e:
                err.append(d)
    else:
        # Get the film name
        scanned = False
        for v in videos:
            video_file_name = os.path.basename(videos[0])
            m = TOOLS.get_movie_info_from_file(video_file_name)
            if m:
                key = "%s%s" % (m.group(1).lower().replace(' ', '.'), m.group(2))
                fulltree[key] = {
                    'dirname': path,
                    'videos': videos
                }
                tree[key] = path
                scanned = True
                break

        if not scanned:
            err.append(path)

def scan_recursive_dir(fulltree, tree, err, stats, path):
    print("----> Scanninng %s" % path)
    videos = glob.glob(os.path.join(glob.escape(path), '*.mp4'))
    videos.extend(glob.glob(os.path.join(glob.escape(path), '*.mkv')))
    videos.extend(glob.glob(os.path.join(glob.escape(path), '*.avi')))
    videos.extend(glob.glob(os.path.join(glob.escape(path), '*.ts')))
    if not videos:
        sub_dirs = [d for d in glob.glob(os.path.join(path, '*')) if os.path.isdir(d)]
        for d in sub_dirs:
            try:
                scan_recursive_dir(fulltree, tree, err, stats, d)
            except Exception as e:
                raise
                #err.append(d)
    else:
        # Get the film name
        basename = os.path.basename(path)
        m = TOOLS.get_movie_info_from_dir(basename)
        if m:
            key = m['key']
            if key in fulltree:
                fulltree[key].setdefault('aux_dirs', []).append(path)
                fulltree[key]['videos'] = get_videos_info(videos, fulltree[key]['videos'])
            else:
                fulltree[key] = {
                    'dirname': path,
                    'videos': get_videos_info(videos),
                    'year': m['year'],
                    'title': m['title']
                }
                tree[key] = path
                
                # Do the stats
                stats['total_movies'] += 1
            
        else:
            err.append(path)

def generate_tree(paths, method):
    fulltree = {}
    tree = {}
    err = []
    stats = {'total_movies': 0}
    if method == 'dir':
        for path in paths:
            scan_recursive_dir(fulltree, tree, err, stats, path)   
    elif method == 'file':
        for path in paths:
            scan_recursive_file(fulltree, tree, err, stats, path)
    else:
        raise Exception('Scanning method is unrecognizable: %s' % method)

    return {'detail': fulltree, 'brief': tree, 'error': err, 'stats': stats}


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--paths', type=str, help='Specify the directories to scan for movies, seperate by comma')
    parser.add_argument('--out', type=str, default='', help='Output file')
    parser.add_argument('--method', type=str, default='dir', choices=['file', 'dir'],
                        help='Scan the movies files based on FILENAME or DIRNAME')
    args = parser.parse_args()

    paths = args.paths.split(',')
    movies_db = generate_tree(paths, args.method)
    if movies_db['error']:
        print("======= Directories can't be scanned =============")
        pprint(movies_db['error'])
    if args.out:
        data = {'paths': paths, 'movies_db': movies_db}
        with open(args.out, 'w') as sout:
            json.dump(data, sout, indent=4, sort_keys=True)

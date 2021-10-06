import os, shutil

from tools import file_tools as FTOOLS


# Put videos of the same movie in one directory
def arrange(new_movies, out_dir):
    for m_id, m_info in new_movies.items():
        # Make the target dir
        target_dir = os.path.join(out_dir, "%s (%s)" % (m_info['title'], m_info['year']))
        if not os.path.isdir(target_dir):
            os.makedirs(target_dir)

        for quality, v_info in m_info['videos'].items():
            # Move videos & its subtitle
            if os.path.isfile(v_info['file']):
                shutil.move(v_info['file'], target_dir)
            else:
                print("WARNING: file %s doesn't exist" % v_info['file'])

            for lang, sub in v_info['subtitles'].items():
                if os.path.isfile(sub):
                    shutil.move(sub, target_dir)
                else:
                    print("WARNING: file %s doesn't exits" % sub)

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--movie_db', type=str, help='The input movie db')
    parser.add_argument('--out_dir', type=str, help='Output directory to store the movies')
    parser.add_argument('--action', type=str, choices=['arrange'], help='What kind of actions to do')
    args = parser.parse_args()

    movie_db = FTOOLS.read_json(args.movie_db)
    if args.action == 'arrange':
        arrange(movie_db['movies_db']['detail'], args.out_dir)

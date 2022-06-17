import os, shutil, json, glob, copy

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

def migrate_scan(current_movie_db, movie_db, default_path):
    info = {}
    for m_id, m_info in movie_db['detail'].items():
        m_info['migration_skipped'] = False
        if default_path:
            m_info['migration_target_dir'] = os.path.join(default_path, "%s (%s)" % (m_info['title'], m_info['year']))
        elif m_id in current_movie_db:
            m_info['migration_target_dir'] = current_movie_db[m_id]['dirname']
        else:
            m_info['migration_target_dir'] = None

    return movie_db['detail']

def migrate_move(info):
    for m_id, m_info in info.items():
        # Skip if said so
        if m_info['migration_skipped']:
            print("Skipping %s" % m_info['title'])
            continue

        # Make dir if possible
        if not os.path.isdir(m_info['migration_target_dir']):
            # Is the dirname exist
            dirname = os.path.dirname(m_info['migration_target_dir'])
            if not os.path.isdir(dirname):
                print("\t>>> Parent dir: %s doesn't exits")
                txt = input("\t>>> Type 'yes' to create the directory, others to skip")
                if txt == 'yes':
                    os.makedirs(dirname)
                else:
                    continue

            os.makedirs(m_info['migration_target_dir'])
        
        # Move the files
        print("Migrating movie %s" % m_info['title'])
        for v_quality, v_info in m_info['videos'].items():
            current_dir = os.path.dirname(v_info['file'])
            print("\t>>> Moving files from %s to %s" % (current_dir, m_info['migration_target_dir']))
            files = glob.glob(os.path.join(glob.escape(current_dir), '*'))
            for f in files:
                basename = os.path.basename(f)
                target = os.path.join(m_info['migration_target_dir'], basename)
                if not os.path.isdir(f):
                    shutil.move(f, os.path.join(m_info['migration_target_dir'], basename))
                elif not os.path.isdir(target):
                    shutil.move(f, m_info['migration_target_dir'])
                else:
                    for ff in glob.glob(os.path.join(glob.escape(f), '*')):
                        bb = os.path.basename(ff)
                        tt = os.path.join(target, bb)
                        shutil.move(ff, tt)


def moveout_scan(current_movie_db, movie_db):
    movies_moveout_info = {}
    for m_id, m_info in movie_db.items():
        if m_id in current_movie_db:
            movies_moveout_info[m_id] = copy.deepcopy(current_movie_db[m_id])

            for quality, q_info in movies_moveout_info[m_id]['videos'].items():
                q_info['moveout_skipped'] = False

    return movies_moveout_info

def moveout_move(moveout_info, out_dir):
    for m_id, m_info in moveout_info.items():
        target_dir = os.path.join(out_dir, os.path.basename(m_info['dirname']))
        for v_quality, v_info in m_info['videos'].items():
            if not v_info['moveout_skipped']:
                if not os.path.isdir(target_dir):
                    os.makedirs(target_dir)
                print("\nMoving %s to %s" % (v_info['file'], target_dir))
                shutil.move(v_info['file'], target_dir)
                for sub_name, sub_info in v_info['subtitles'].items():
                    print("Moving %s to %s" % (sub_info, target_dir))
                    shutil.move(sub_info, target_dir)


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--current_movie_db', type=str, help='The input of current movie db')
    parser.add_argument('--movie_db', type=str, help='The input movie db')
    parser.add_argument('--out_dir', type=str, help='Output directory to store the movies')

    parser.add_argument('--migrate_info', type=str, help='In/out information for migrating files')
    parser.add_argument('--migrate_default_path', type=str, help='Default path for moving the movies to')

    parser.add_argument('--moveout_info', type=str, help='In/out information for moveout files')
    parser.add_argument('--action', type=str, choices=['arrange', 'migrate_scan', 'migrate_move', 'moveout_scan', 'moveout_move'], help='What kind of actions to do')
    args = parser.parse_args()

    movie_db = FTOOLS.read_json(args.movie_db)
    if args.action == 'arrange':
        if not args.out_dir:
            raise Exception("Arrange action needs --out_dir value set")
        arrange(movie_db['movies_db']['detail'], args.out_dir)

    if args.action in ['migrate_scan', 'migrate_move']:
        if not args.migrate_info:
            raise Exception("Migrate action needs --migrate_info value set")

        if args.action == 'migrate_scan':
            current_movie_db = FTOOLS.read_json(args.current_movie_db)
            info = migrate_scan(current_movie_db['movies_db']['detail'], movie_db['movies_db'], args.migrate_default_path)
            with open(args.migrate_info, 'w') as sout:
                sout.write(json.dumps(info, indent=4))

        if args.action == 'migrate_move':
            with open(args.migrate_info) as sin:
                info = json.load(sin)

            migrate_move(info)

    if args.action in ['moveout_scan', 'moveout_move']:
        if not args.moveout_info:
            raise Exception("Moveout scan actions need --moveout_info value set")
        
        if args.action == 'moveout_scan':
            current_movie_db = FTOOLS.read_json(args.current_movie_db)
            movies_moveout_info = moveout_scan(current_movie_db['movies_db']['detail'], movie_db['movies_db']['detail'])
            with open(args.moveout_info, 'w') as sout:
                sout.write(json.dumps(movies_moveout_info, indent=4))

        if args.action == 'moveout_move':
            if not args.out_dir:
                raise Exception("Moveout move actions need --out_dir value set")
            movies_moveout_info = FTOOLS.read_json(args.moveout_info)
            moveout_move(movies_moveout_info, args.out_dir)




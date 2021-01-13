import os, re, glob, json

def lang_code(lang):
    if lang == 'Vietnamese':
        return 'vie'
    if lang == 'English':
        return 'eng'
    return 'unk'

def create_link(src, link):
    # If the link already exits
    if os.path.islink(link):
        # Re create the link it is incorrect
        if os.readlink(link) != src:
            os.unlink(link)
            os.symlink(src, link)
    else:
        os.symlink(src, link)

def remove_obs_dirs(obs_dirs):
    for d in obs_dirs:
        links = glob.glob(os.path.join(glob.escape(d), '*'))
        for l in links:
            os.unlink(l)
        os.rmdir(d)

def get_tag(quality, team):
    ls = quality.split('.')
    if ls[0] != '2160p':
        return quality

    if team != 'YIFY' and not team in quality:
        return "%s.%s" % (quality, team)
    else:
        return quality

def generate_symlinks(movies, path, limit=0):
    idx = 0
    current_dirs = set(glob.glob(os.path.join(glob.escape(path), '*')))
    new_dirs = set()
    for key, movie in movies.items():
        if limit > 0 and idx >= limit:
            break
        idx += 1

        print("-----> Creating links for %s" % key)
        name = "%s (%s)" % (movie['title'], movie['year'])
        movie_dir = os.path.join(path, name)
        if not os.path.isdir(movie_dir):
            os.mkdir(movie_dir)

        # Generate the symbolinks
        current_links = set(glob.glob(os.path.join(glob.escape(movie_dir), '*')))
        new_links = set()
        for sub_key, video in movie['videos'].items():
            tag = get_tag(sub_key, video['team'])
            v_format = video['file'].rsplit('.', 1)[1]
            v_link = os.path.join(movie_dir, "%s - %s.%s" % (name, tag, v_format))
            create_link(video['file'], v_link)
            new_links.add(v_link)

            # Generate links for subtitles
            for lang, sub_file in video['subtitles'].items():
                sub_format = sub_file.rsplit('.', 1)[1]
                sub_link = os.path.join(movie_dir, "%s - %s.%s.%s" % (name, tag, lang_code(lang), sub_format))
                create_link(sub_file, sub_link)
                new_links.add(sub_link)

        # Remove obsolete links
        obs_links = current_links.difference(new_links)
        for l in obs_links:
            os.unlink(l)

        # Add new dir to list
        new_dirs.add(movie_dir)

    # Remove obsolete dirs
    obs_dirs = current_dirs.difference(new_dirs)
    remove_obs_dirs(obs_dirs)


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--path', type=str, help='Location to create symbolic links')
    parser.add_argument('--movies_db', type=str, help='Movies db file')
    parser.add_argument('--limit', type=int, default=0, help='Number of movies to create links')
    args = parser.parse_args()

    with open(args.movies_db) as sin:
        movies_db = json.load(sin)

    generate_symlinks(movies_db['movies_db']['detail'], args.path, args.limit)



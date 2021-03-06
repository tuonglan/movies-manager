import os, glob, re, json, shutil
from pprint import pprint


PTT = re.compile('(.+?)\.((?:19|20)\d\d)\.(.+)')
PTT_YTS = re.compile('(.+?)\((\d\d\d\d)\)(.+)')

def copy_subtitles(movies_db, exe=False):
    sub_data = {'subtitles': {}, 'no-sub': [], 'cmds': {}}

#    for d in glob.glob(os.path.join(path, '*')):
#        dir_name = os.path.basename(d).lower()
#        print("\n-------- Processing %s ---------" % dir_name)
#        if is_yts:
#            m = PTT_YTS.match(dir_name)
#            name = m.group(1).rstrip().replace(' ', '.')
#            quality = '2160p' if '2160' in m.group(3) else '1080p'
#            codec = 'x265'
#        else:
#            m = PTT.match(dir_name)
#            name = m.group(1).lower()
#            quality = '2160p' if '2160p' in m.group(3) else '1080p'
#            codec = 'x265' if 'x265' in m.group(3) else 'h264'
#        
#        key = "%s.%s" % (name, m.group(2))
#        sub_key = "%s_%s" % (quality, codec)
#        sub_data['subtitles'].setdefault(key, {})

    for mov_name, mov_data in movies_db.items():
        sub_data['subtitles'].setdefault(mov_name, {})
        for mov_format, mov_path in mov_data['new'].items():
            sub = {'English': None, 'Vietnamese': None}
            cmd = []
            videos = glob.glob(os.path.join(glob.escape(mov_path), '*.mp4'))
            if not videos:
                videos = glob.glob(os.path.join(glob.escape(mov_path), '*.mkv'))
            mp4_file = videos[0]
            mp4_name = os.path.splitext(os.path.basename(mp4_file))[0]

            # Copy subtitles from Subs: English
            if os.path.isdir(os.path.join(mov_path, 'Subs')):
                srts = glob.glob(os.path.join(glob.escape(mov_path), 'Subs/*.srt'))
                biggest_file = None
                for srt in srts:
                    if not biggest_file or os.path.getsize(srt) > os.path.getsize(biggest_file):
                        if os.path.getsize(srt) > 15000:
                            biggest_file = srt

                if biggest_file:
                    new_eng_sub_file = os.path.join(mov_path, "%s.eng.srt" % mp4_name)
                    cmd.append("English Sub: %s FROM %s, size: %s" % (new_eng_sub_file, biggest_file, os.path.getsize(biggest_file)))
                    sub['English'] = "%s (New)" % new_eng_sub_file
                    if exe:
                        shutil.copyfile(biggest_file, new_eng_sub_file)
                        
            # Copy subtitles from current movies
            current_m_d = movies_db[mov_name]['current']
            if current_m_d:
                srts = glob.glob(os.path.join(glob.escape(current_m_d), '*.srt'))
                srts.extend(glob.glob(os.path.join(glob.escape(current_m_d), '*.ass')))
                for srt in srts:
                    ext = os.path.splitext(srt)[1]
                    if ('vie.' in srt or '(Vietnamese)' in srt or '(Vie)' in srt) and not sub['Vietnamese']:
                        new_vie_sub_file = os.path.join(mov_path, "%s.vie%s" % (mp4_name, ext))
                        cmd.append("Vietnamese Sub: %s FROM %s" % (new_vie_sub_file, srt))
                        sub['Vietnamese'] = "%s (Current)" % new_vie_sub_file
                        if exe:
                           shutil.copyfile(srt, new_vie_sub_file)
                    if ('eng.' in srt or '(English)' in srt or len(srts) < 3) and not sub['English']:
                        new_eng_sub_file = os.path.join(mov_path, "%s.eng%s" % (mp4_name, ext))
                        cmd.append("English Sub: %s FROM %s" % (new_eng_sub_file, srt))
                        sub['English'] = "%s (Current)" % new_eng_sub_file
                        if exe:
                            shutil.copyfile(srt, new_eng_sub_file)

            if not sub['English'] and not sub['Vietnamese']:
                sub_data['no-sub'].append("%s.%s" % (mov_name, mov_format))
            else:
                sub_data['subtitles'][mov_name][mov_format] = sub
            sub_data['cmds']["%s.%s" % (mov_name, mov_format)] = cmd

    return sub_data


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--new_movies_db', type=str, help='Movies DB file')
    parser.add_argument('--out', type=str, default='', help='Output file')
    parser.add_argument('--exe', action='store_true', help='Execute or just show')
    args = parser.parse_args()

    with open(args.new_movies_db) as sin:
        movies_db = json.load(sin)

    sub_data = copy_subtitles(movies_db['movies_db'], args.exe)

    if args.out:
        with open(args.out, 'w') as sout:
            json.dump(sub_data, sout, indent=4, sort_keys=True)





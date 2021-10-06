import os, copy
import pysubparser, langdetect
from pysubparser import parser as SubParser

from tools import language_tools as LTOOLS
from tools import file_tools as FTOOLS
from tools import subtitle_tools as SUBTOOLS

def match_file_with_lang(sub_files, lang_iso):
    # Match based on the full language name & alpha_3
    def _sublist_of_generator(gen, start, end):
        ls = []
        try:
            for i in range(start):
                next(gen)
            for i in range(end-start):
                ls.append(next(gen))
        except:
            pass

        return ls

    for f in sub_files:
        sub_basename = os.path.basename(f).lower()
        if lang_iso.name.lower() in sub_basename:
            return f
        if sub_basename.rsplit('.', 1)[0].endswith(lang_iso.alpha_3):
            return f

    # Match based on the content of the text
    #print("Search %s using content of : %s" % (lang_iso.name, sub_files))
    for f in sub_files:
        # Get 30 subtitles in the middle
        subtitles = [s.text.strip() for s in _sublist_of_generator(SubParser.parse(f), 10, 41)]
        detected_lang = langdetect.detect('. '.join(subtitles))
        if detected_lang == lang_iso.alpha_2:
            return f

    return None

def scan_subtitles(movies_db, new_movies, langs, langs_content_detect):
    subtitles_info = copy.deepcopy(new_movies)

    # Each movies
    for movie_key, m_info in subtitles_info.items():
        video_no_sub = []
        video_sub = {}
        
        
        # Each versions
        for quality, v_info in m_info['videos'].items():
            # Scan the current Subs directory
            sub_dir = os.path.join(os.path.dirname(v_info['file']), 'Subs')
            sub_files = FTOOLS.files_with_extensions(sub_dir, ['srt', 'ass'])

            # Select appropriate sub for a language in current Subs
            for lang in langs:
                lang_iso = LTOOLS.language_iso(lang)
                if not v_info['subtitles'].setdefault(lang_iso.name, None) and lang in langs_content_detect:
                    v_info['subtitles'][lang_iso.name] = match_file_with_lang(sub_files, lang_iso)
                
                # Save the language information if subtitles are in Subs
                if v_info['subtitles'][lang_iso.name]:
                    video_sub.setdefault(v_info['source'], {}).setdefault(lang_iso.name, v_info['subtitles'][lang_iso.name])
                else:
                    video_no_sub.append(v_info)

        # Seach subtitle again for video without subtitles
        for v_info in video_no_sub:
            for lang in langs:
                lang_iso = LTOOLS.language_iso(lang)

                # Get from Subs
                if not v_info['subtitles'][lang_iso.name] and video_sub.get(v_info['source'], {}).get(lang_iso.name):
                    v_info['subtitles'][lang_iso.name] = video_sub[v_info['source']][lang_iso.name]

                # Get from movie_db
                if not v_info['subtitles'][lang_iso.name] and movies_db.get(movie_key):
                    for quality, v_info_in_db in movies_db[movie_key]['videos'].items():
                        if v_info_in_db['source'] == v_info['source'] and v_info_in_db['subtitles'].get(lang_iso.name):
                            v_info['subtitles'][lang_iso.name] = v_info_in_db['subtitles'][lang_iso.name]

    return subtitles_info

def copy_subtitles(subtitles_info, is_forced=False):
    # Each movie, each video, each language
    for movie_key, m_info in subtitles_info.items():
        for quality, v_info in m_info['videos'].items():
            for lang, link in v_info['subtitles'].items():
                lang_alpha_3 = LTOOLS.language_iso(lang).alpha_3
                if not link:
                    continue
                if not is_forced and SUBTOOLS.exits(v_info['file'], lang_alpha_3):
                    continue

                if link.startswith("http"):
                    SUBTOOLS.download_sub_to_file(link, v_info['file'], lang_alpha_3)
                else:
                    SUBTOOLS.copy(link, v_info['file'], lang_alpha_3)


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--movies_db', type=str, help='JSON file of current movie database')
    parser.add_argument('--new_movies', type=str, help='JSON file of new movies')
    parser.add_argument('--subtitles_info', type=str, help='Subtitles information file (for both input & output)')
    parser.add_argument('--languages', type=str, default='eng,vie', help='Specify languages in ISO ALPHA_3, separated by ","')
    parser.add_argument('--languages_content_detect', type=str, default='eng', 
                        help='Languages which allow the scanner to look into the content to detect the language')
    parser.add_argument('--action', type=str, choices=['scan', 'copy'], help='Scanning for subittle info or copy subtitles')
    parser.add_argument('--force', action='store_true', help='Force overwriting if needed')
    args = parser.parse_args()

    # Scann the movies
    movies_db = FTOOLS.read_json(args.movies_db)['movies_db']['detail']
    new_movies = FTOOLS.read_json(args.new_movies)['movies_db']['detail']
    langs = args.languages.split(',')
    langs_content_detect = args.languages_content_detect.split(',')

    if args.action == 'scan':
        subtitles_info = scan_subtitles(movies_db, new_movies, langs, langs_content_detect)
        FTOOLS.write_json(subtitles_info, args.subtitles_info)
    if args.action == 'copy':
        subtitles_info = FTOOLS.read_json(args.subtitles_info)
        copy_subtitles(subtitles_info, args.force)

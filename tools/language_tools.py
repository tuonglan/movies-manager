import pycountry


def language_iso(lang):
    if len(lang) < 2:
        raise Exception("Input language name should be at least 2 characters")
    elif len(lang) == 2:
        country = pycountry.langagues.get(alpha_2=lang)
    elif len(lang) == 3:
        country = pycountry.languages.get(alpha_3=lang)
    else:
        country = pycountry.languages.get(name=lang)

    return country

def language_standardize(lang, target='name'):
    country = language_iso(lang)

    # Return the languages
    if target == 'name':
        country.name
    elif target == 'alpha_2':
        country.alpha_2
    elif target == 'alpha_3':
        country.alpha_3
    else:
        raise Exception("Invalid language ISO target")


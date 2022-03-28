import re

def clean_text(text: str) -> str:
    """Clean-up text
    Removes nasty stuff from texts in order to prepare them
    for modelling.
    Args:
        text (str): Text to clean.
    Returns:
        str: cleaned text.
    """

    # clean up text
    replace_with_space = [
        # HTML Links
        "<a href.*?<\/a>",
        # various HTML
        # <h5> <i> etc.
        r'\<[^)]*\>',
        # /ritzau/ etc.
        r'/[^)]*/',
        # &mdash; etc.
        "&[^)]*;",
        # links
        # HACK: FIX. Og erstat med punktummer?
        '\\n',
        '\\t',
        '\\xa0',
        # TODO: overvej denne.
        "--------- SPLIT ELEMENT ---------"
        ]

    replace_with_space = "|".join(replace_with_space)
    
    text = re.sub(replace_with_space, " ", text)

    # replace the over spaces.
    text = re.sub('\s{2,}', " ", text)

    return text

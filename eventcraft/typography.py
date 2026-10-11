"""Portable art-directed font contracts; font files are never redistributed."""
import json
from importlib.resources import files


def typography(style: str) -> dict:
    return json.loads(files('eventcraft').joinpath('data/typography.json').read_text(encoding='utf-8'))[style]


def typography_css(style: str) -> str:
    t = typography(style)
    def stack(names):
        return ','.join(json.dumps(n) for n in names) + ',' + t['generic']
    return f'''h1{{font-family:{stack(t['en_title'] + t['zh_title'])};font-weight:{t['weight']};
font-style:{t['shape']};letter-spacing:{t['tracking']}em;line-height:{t['leading']};}}
.subtitle,.greeting{{font-family:{stack(t['subtitle'])};}}
.details,.credit,.cta,.edition{{font-family:{stack(t['information'])};}}
.fact[data-field=when] p,.serial{{font-family:{stack(t['numbers'])};font-variant-numeric:tabular-nums;}}
h1{{line-break:strict;word-break:normal;text-wrap:balance;}}
.subtitle{{line-break:strict;}}'''

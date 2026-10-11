"""One pre-generation composition contract drives both ImageGen and typesetting."""
import math
import re

from .schema import Event
from .visuals import systems


def composition(event: Event, style: str, ratio: str = 'portrait') -> dict:
    system = systems()[style]
    # Approximate display units before the host can measure real platform fonts.
    units = sum(1 if re.match(r'[\u3400-\u9fff]', c) else .52 for c in event.title)
    compact = units > 18
    lower = style in {'editorial-minimal', 'academic-clean', 'sports-dynamic'}
    middle = style == 'luxury-elegant'
    title_y = .46 if lower else .28 if middle else .09
    title_h = min(.37, .23 + max(0, math.ceil(units / 8)-2) * .04)
    if lower and compact:
        title_y = max(.30, .67-title_h)
    if middle:
        title_h = min(.37, title_h + .06)
    zones = {'title': [.07, title_y, .86, title_h],
             'facts': [.07, .80, .86, .095], 'cta': [.07, .915, .86, .05]}
    if ratio == 'square':
        zones = {'title': [.07, .09 if not lower else .39, .86, .29 if not compact else .36],
                 'facts': [.07, .79, .86, .12], 'cta': [.07, .925, .86, .04]}
        if lower and compact:
            zones['title'][1] = .32
    focus = 'upper third' if lower else 'lower middle, between the headline and facts'
    if middle:
        focus = 'perimeter, leaving the center unobstructed'
    return {'version': 3, 'ratio': ratio, 'zones': zones, 'compact': compact,
            'title_units': round(units, 2), 'title_max_lines': max(2, math.ceil(units/8)),
            'focal_position': focus, 'layout': system['layout'],
            'reading_tone': system.get('reading_tone', 'dark'),
            'adaptation': 'extend natural negative space before reducing type; never add opaque rescue panels'}


def composition_css(event: Event, style: str, ratio: str) -> str:
    c = composition(event, style, ratio)
    result = ''
    for zone, rect in c['zones'].items():
        selector = {'title': '.heading', 'facts': '.details', 'cta': 'footer'}[zone]
        x, y, w, h = [v*100 for v in rect]
        result += f'.poster {selector}{{left:{x}%;top:{y}%;width:{w}%;height:{h}%;}}'
    return result

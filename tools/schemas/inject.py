"""Insère (ou met à jour) un schéma dans une fiche Markdown.

Chaque schéma est encadré par <!-- schema:nom --> ... <!-- /schema:nom -->,
ce qui permet de relancer le script sans dupliquer : le bloc est remplacé.
"""
import re

import os
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'src', 'content', 'fiches')


def block(sid, html):
    return f'<!-- schema:{sid} -->\n{html}\n<!-- /schema:{sid} -->'


def apply(text, sid, html, fence=None, before=None, after=None):
    b = block(sid, html)
    m = re.search(rf'<!-- schema:{re.escape(sid)} -->.*?<!-- /schema:{re.escape(sid)} -->', text, re.S)
    if m:
        return text[:m.start()] + b + text[m.end():]
    if fence:
        # le bloc de code ``` ... ``` qui contient ce texte
        for fm in re.finditer(r'^```[^\n]*\n.*?^```[ \t]*$', text, re.S | re.M):
            if fence in fm.group(0):
                return text[:fm.start()] + b + text[fm.end():]
        raise ValueError(f'{sid}: bloc introuvable ({fence!r})')
    lines = text.split('\n')
    anchor = before or after
    # on ne cherche qu'après le frontmatter
    fm_end = [i for i, l in enumerate(lines) if l.strip() == '---'][1]
    for i in range(fm_end + 1, len(lines)):
        if lines[i].startswith(anchor):
            if before:
                lines[i:i] = [b, '']
            else:
                lines[i + 1:i + 1] = ['', b]
            return '\n'.join(lines)
    raise ValueError(f'{sid}: ancre introuvable ({anchor!r})')


def put(path, sid, html, **kw):
    full = f'{BASE}/{path}'
    text = open(full).read()
    new = apply(text, sid, html, **kw)
    if new != text:
        open(full, 'w').write(new)

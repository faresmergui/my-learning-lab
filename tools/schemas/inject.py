"""Inserts (or updates) a diagram in a Markdown note.

Each diagram is wrapped in <!-- schema:name --> ... <!-- /schema:name -->,
so the script can be re-run without duplicating anything: the block is replaced.
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
        # the ``` ... ``` code block that contains this text
        for fm in re.finditer(r'^```[^\n]*\n.*?^```[ \t]*$', text, re.S | re.M):
            if fence in fm.group(0):
                return text[:fm.start()] + b + text[fm.end():]
        raise ValueError(f'{sid}: bloc introuvable ({fence!r})')
    lines = text.split('\n')
    anchor = before or after
    # only search after the frontmatter
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

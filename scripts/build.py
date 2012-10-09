#!/usr/bin/env python
# -*- coding: latin-1 -*-

import pyinotify
import re
import json
import codecs
from unicodedata import normalize

langs = ['fr', 'en']

#credit for this method and regex : http://flask.pocoo.org/snippets/5/
_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def slugify(text, delim=u'-'):
    """Generates an ASCII-only slug."""
    result = []
    for word in _punct_re.split(unicode(text).lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result)).encode('ascii')


entry_line_re = re.compile(r'\[(\w*)(\|(\w*)){0,1}\] (.*)')
following_line_re = re.compile(r'  (.*)')


def build():

    # parse experiences file
    f = codecs.open('experiences.textdb', encoding='utf-8')
    exps = []
    line = f.readline()
    while line:
        if line.strip() == '###':
            exp = {}
            prop = {}
            while 1:
                next_line = f.readline()
                # append to previous value if it's a following line
                following_res = following_line_re.match(next_line)
                if following_res:
                    prop['value'] += following_res.group(1).strip()
                else:
                    if prop:
                        # save in-memory property, and clear it
                        if prop['lang']:
                            if not prop['field'] in exp.keys():
                                exp[prop['field']] = {}
                            exp[prop['field']][prop['lang']] = prop['value'].strip()
                        else:
                            exp[prop['field']] = prop['value'].strip()
                        prop = {}
                    # start new property if line matches format
                    entry_res = entry_line_re.match(next_line)
                    if entry_res:
                        prop['field'] = entry_res.group(1)
                        prop['lang'] = entry_res.group(3)
                        prop['value'] = entry_res.group(4)
                    else:
                        # line doesn't match anything, save current experience, and skip to next
                        # but first, do some further computing with slugs and keywords
                        if exp['keywords'] != "/":
                            exp['keywords'] = exp['keywords'].split(',')
                        else:
                            exp['keywords'] = []
                        exp['keywords_slugs'] = map(slugify, exp['keywords'])
                        exp['title_slug'] = {}
                        for lang in exp['title']:
                            exp['title_slug'][lang] = slugify(exp['title'][lang])
                        exps.append(exp)
                        break
        line = f.readline()

    # parse contents file
    f = codecs.open('contents.textdb', encoding='utf-8')
    contents = {}
    next_line = True
    while next_line:
        next_line = f.readline()
        entry_res = entry_line_re.match(next_line)
        # start new entry if line matches format
        if entry_res:
            string_id = entry_res.group(1)
            lang = entry_res.group(3)
            value = entry_res.group(4)
            if not string_id in contents:
                contents[string_id] = {}
            contents[string_id][lang] = value

    # merge keywords lists
    kw_list = []
    for exp in exps:
        kw_list = kw_list + exp['keywords_slugs']
    # remove doublons, sort alphabetically
    kw_list = list(set(kw_list))
    kw_list.sort()

    # create reverse experiences list by keywords
    exp_lookup_list = {}
    for lang in langs:
        exp_lookup_list[lang] = dict()
        for kw in kw_list:
            exp_lookup_list[lang][kw] = []
    for exp in exps:
        for kw in exp['keywords_slugs']:
            for lang in langs:
                exp_lookup_list[lang][kw].append(exp['title_slug'][lang])
    # print exp_lookup_list

    # read the experience template file
    o = open("experience-template.html")
    template = o.read()

    exp_html = {}
    for lang in langs:
        # increment template with each experience
        exp_cpt = 0
        exp_html[lang] = ''
        for exp in exps:
            inc_template = template
            inc_template = template.replace('%title%', exp['title'][lang])
            inc_template = inc_template.replace('%title_slug%', exp['title_slug'][lang])
            inc_template = inc_template.replace('%subtitle%', exp['subtitle'][lang])
            inc_template = inc_template.replace('%date%', exp['date'])
            inc_template = inc_template.replace('%type%', exp['type'])
            inc_template = inc_template.replace('%description%', exp['description'][lang])
            inc_template = inc_template.replace('%keywords_slugs%', ','.join(exp['keywords_slugs']))
            even_odd_str = 'odd'
            if exp_cpt % 2 == 0:
                even_odd_str = 'even'
            inc_template = inc_template.replace('%even_or_odd%', even_odd_str)
            exp_cpt += 1
            exp_html[lang] += inc_template

    # read the keywords template file
    o = open("keyword-template.html")
    template = o.read()
    # increment template for each keyword
    kw_html = ''
    for kw in kw_list:
        inc_template = template.replace('%slug%', kw)
        inc_template = inc_template.replace('%title%', kw)
        kw_html += inc_template

    # increment the layout file
    layout_file = codecs.open("layout.html")
    layout = layout_file.read()
    for lang in langs:
        # lang
        lang_html = "<li class='selected'><a href='#' class='" + lang + "'>&nbsp;</a></li>"
        for lang_bis in langs:
            if lang_bis != lang:
                filename = "index.html"
                if lang_bis != "en":
                    filename = "index." + lang_bis + ".html"
                lang_html += "<li><a href='" + filename + "' class='" + lang_bis + "'>&nbsp;</a></li>"
        inc_layout = layout.replace('%LANGUAGES%', lang_html)

        inc_layout = inc_layout.replace('%EXPERIENCES%', exp_html[lang])
        inc_layout = inc_layout.replace('%KEYWORDS%', kw_html)
        inc_layout = inc_layout.replace('%lookup_table_json%', json.dumps(exp_lookup_list[lang]))
        # replace contents strings from the textdb
        for string_id in contents:
            inc_layout = inc_layout.replace('%' + string_id + '%', contents[string_id][lang])
        # output to new file
        filename = "index"
        if lang != 'en':
            filename += "." + lang
        index_file = codecs.open(filename + ".html", "w", encoding='utf-8')
        index_file.write(inc_layout)


# This handler will be used to report and process events
class EventHandler(pyinotify.ProcessEvent):
    def process_IN_MODIFY(self, event):
        print "file updated:", event.pathname
        build()

# Instanciate a new WatchManager (will be used to store watches).
wm = pyinotify.WatchManager()
handler = EventHandler()
notifier = pyinotify.Notifier(wm, handler)

for filename in ['experience-template.html', 'experiences.textdb', 'contents.textdb', 'layout.html', 'keyword-template.html']:
    wm.add_watch(filename, pyinotify.IN_MODIFY)

# initial building
build()

# Loop forever and handle events.
notifier.loop()

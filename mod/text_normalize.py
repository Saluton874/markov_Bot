#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import re, unicodedata
import demoji
'''
from text_normalize import normalize
'''
#tag_regexp = re.compile(r"#(\w+)")

def unicode_normalize(cls, s):
    pt = re.compile('([{}]+)'.format(cls))
    def norm(c):
        return unicodedata.normalize('NFKC', c) if pt.match(c) else c
    s = ''.join(norm(x) for x in re.split(pt, s))
    s = re.sub('－', '-', s)
    return s

def remove_extra_spaces(s):
    s = re.sub('[ 　]+', ' ', s)
    blocks = ''.join(('\u4E00-\u9FFF',  # 日中韓 合同化された表意文字
                      '\u3040-\u309F',  # ひらがな
                      '\u30A0-\u30FF',  # カタカナ
                      '\u3000-\u303F',  # 日中韓 記号と句読点
                      '\uFF00-\uFFEF'   # 半角と全角
                      ))
    basic_latin = '\u0000-\u007F'
    def remove_space_between(cls1, cls2, s):
        p = re.compile('([{}]) ([{}])'.format(cls1, cls2))
        while p.search(s):
            s = p.sub(r'\1\2', s)
        return s
    
    s = remove_space_between(blocks, blocks, s)
    s = remove_space_between(blocks, basic_latin, s)
    s = remove_space_between(basic_latin, blocks, s)
    return s

def normalize(s):
    s = s.strip()
    s = demoji.replace(string=s, repl="")
    s = unicode_normalize('０-９Ａ-Ｚａ-ｚ｡-ﾟ', s)
    def maketrans(f, t):
        return {ord(x): ord(y) for x, y in zip(f, t)}
    s = re.sub('[˗֊‐‑‒–⁃⁻₋−]+', '-', s)
    s = re.sub('[﹣－ｰ—―─━ー]+', 'ー', s)
    s = re.sub('\.\.\.|・・・', '…', s)
    s = re.sub('[~∼∾〜〰～]', '', s)
    s = re.sub(r'\[ tpl \].*?\[/ tpl \]', '', s)
    s = re.sub(r'\=\=.*?\=\=', '', s)
    s = re.sub(r'\=\=\=.*?\=\=\=', '', s)
    s = re.sub(r'\(.*?\)', '', s)
    s = re.sub(u'（.*?）', '', s)
    s = re.sub(r'\{\{', '', s)
    s = re.sub(r'\}\}', '', s)
    s = re.sub(r'\[\[.*?\]\]', '', s)
    s = re.sub(r'\[.*?\]', '', s)
    s = re.sub(r'\|.*?\|', '', s)
    s = re.sub(r'|\n|', '', s)
    s = re.sub(r'@[0-9a-zA-Z_]{1,15}(RT){0,1}', '', s)
    s = re.sub(r"/[\[\]\{\}\*\"\'\|]+/u", '', s) 
    s = re.sub(r'《[^》]*》|＝＝[^＝＝]*＝＝|（[^）]*）|【[^】]*】|<[^>]*>', '', s) # カッコ内を除去
    s = re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', '', s) # URLを除去
    s = s.translate(
        maketrans('!"#$%&\'()*+,-./:;<=>?@[¥]^_`{|}~｡､･｢｣',
              '！”＃＄％＆’（）＊＋，－．／：；＜＝＞？＠［￥］＾＿｀｛｜｝〜。、・「」'))
    s = remove_extra_spaces(s)
    s = unicode_normalize('！”＃＄％＆’（）＊＋，－．／：；＜＞？＠［￥］＾＿｀｛｜｝〜', s)  # keep ＝,・,「,」
    s = re.sub('[’]', '\'', s)
    s = re.sub('[”]', '"', s)
    s = re.sub(r'^RT\:', '', s)
    #s = tag_regexp.findall(s)
    s = re.sub(r'#(\w+)','',s) 

    return s

if __name__ == '__main__':
    while True:
        user = input('テキストを入力')
        try:
            if user == ':q': break
            print(normalize(user))
        except:
            print()
            break
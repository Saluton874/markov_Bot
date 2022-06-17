# -*- coding: utf-8 -*-
import os, sqlite3
class d:
    path       = os.path.abspath(os.path.dirname(__file__))+'/'
    mecab_dic  = '-d /home/hanayo/src/mecab-ipadic-neologd/'
def negaposi(word_li):
    ''' 極性判断 テキストは-F%[6]でリスト化されたもの '''
    conn   = sqlite3.connect(d.path+'db/単語感情極性対応表.db')
    c      = conn.cursor()
    li     = []
    for i, word in enumerate(word_li):
        try: c.execute('SELECT 数値 FROM 単語感情極性対応表 WHERE 単語=?', (word,))
        except: pass
        else:
            float_tuple = c.fetchone()
            if type(float_tuple) == tuple: li.append(float_tuple[0])
    conn.close()
    try:
        return sum(li)/len(li)
    except: return 0
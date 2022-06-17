#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
def load_file_no_enter(path):
    ''' ファイルを開き、改行を無くす '''
    li = []
    with open(path, 'r') as f: li.extend([l.rstrip('\r\n') for l in f])
    return ''.join(li)

def text_list(path):
    ''' ファイルを読み込みリスト化する '''
    ''' ['テスト', 'テスト2', 'テスト3', 'テスト4'] '''
    lists = []
    with open(path, 'r') as f:
        for l in f:
            lists.append(l.rstrip('\r\n')) 
    return lists

def tsv_list(path):
    ''' TSVファイルを入れ子でリスト化 '''
    ''' [['テスト', 'テスト'], ['テスト2', 'テスト2']] '''
    lists = []
    with open(path, 'r') as f:
        for l in f:
            lists.append([item.rstrip('\r\n') for item in l.split('\t')]) 
    return lists

def split_str(s, n):
    "n文字ずつのリストを返す"
    length = len(s)
    return [s[i:i+n] for i in range(0, length, n)]
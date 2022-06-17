#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os, json, re, random, datetime
import tweepy
import numpy as np
import MeCab
from mod.text_normalize import normalize as nor
from mod.file import split_str, text_list
from glob import glob
JST = datetime.timezone(datetime.timedelta(hours=9), "JST")

class d:
	path	   = os.path.abspath(os.path.dirname(__file__))+'/'
	dict_file  = path+'files/markov_train_{}.json'
	word_file  = path+'files/words.txt'
	docments   = path+'docments/'
	mecab_dic  = '-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd/'
	eos		= ['','。','♡','☆','♪','?','!']
	dic_re	 = json.load(open(path+'files/re.json',"r"))
	dic_tag	= dic_re.keys() # TSVから読み込むタグ
	re_ngword = path+'ngword.txt'

API = json.load(open(d.path+'api.json',"r"))
time_now = datetime.datetime.now(JST)
check_days = 1

# APIの認証
auth = tweepy.OAuthHandler(API['ConsumerKey'], API['ConsumerSecret'])
auth.set_access_token(API['AccessToken'], API['AccessTokenSecret'])
api = tweepy.API(auth)

with open('re_ngword.txt', 'r') as f:
    '''NGワードリストを読み込む'''
    re_ng = ''
    for l in f: re_ng += l.rstrip('\r\n')

class mecab:
	@staticmethod
	def option(text,option='-Owakati'):
		m = MeCab.Tagger(d.mecab_dic+' '+option).parse(text).rstrip('\n')
		return m.split() if option == '-Owakati' else m
	@classmethod
	def mecab_plus(cls, text, 内容語 = False):
		''' 名詞と動詞を複合化またはそれ以外を除外 '''
		terms = []
		nodes = cls.option(nor(text),'-F%m,%f[0],%f[1],').split(',')
		nodes = split_str(nodes,3)
		for idx, node in enumerate(nodes):
			if idx == 0:
				terms.append(node[0])
				continue
			try:
				# 名詞を複合化
				if node[1] == "名詞" and nodes[idx-1][1] == "名詞" and (nodes[idx-1][2] != "接尾" or nodes[idx-1][2] == "接尾"): #or\
					#nodes[idx-1][1] == "動詞" and (node[1] == "助詞" or node[1] == "助動詞") or (node[2] == "副助詞"):
					terms = terms[:-1]
					terms.append(nodes[idx-1][0]+node[0])
				else:
					if 内容語 == True:
						if node[1] in ['名詞','動詞'] and not node[2] in ['接尾','助動詞']: terms.append(node[0])
					else:
						terms.append(node[0])
			except IndexError: pass
		return terms


class markov:
	''' マルコフ連鎖 '''
	@classmethod
	def register_dic(cls, words):
		words = mecab.mecab_plus(words)
		cls.dic
		size = 3
		words_len = len(words)
		if len(words) == 0: return
		tmp = ["@"]
		for word in words:
			if word in '': continue
			tmp.append(word)
			if words_len < size and words_len < len(tmp):
				for _ in range(size - words_len -1):
					tmp.append('。')
			else:
				if len(tmp) < size: continue
				if len(tmp) > size: tmp = tmp[1:]
			cls.__set_word(cls.dic, tmp)

	@staticmethod
	def __set_word(dic, tmp):
		w1, w2, w3 = tmp
		if not w1 in dic: dic[w1] = {}
		if not w2 in dic[w1]: dic[w1][w2] = {}
		if not w3 in dic[w1][w2]: dic[w1][w2][w3] = 0
		dic[w1][w2][w3] += 1

	@classmethod
	def make_sentence(cls,head):
		if not head in cls.dic: return ''
		ret = []
		if head != "@": ret.append(head)
		top = cls.dic[head]
		w1 = cls.__word_choice(top)
		w2 = cls.__word_choice(top[w1])
		ret.append(w1)
		ret.append(w2)
		while True:
			if w1 in cls.dic and w2 in cls.dic[w1]:
				w3 = cls.__word_choice(cls.dic[w1][w2])
			else:
				w3 = ''
			ret.append(w3)
			if w3 in d.eos: break
			w1, w2 = w2, w3
		return ''.join(ret)

	w = 0 # 重さ
	@classmethod
	def __enumkeys(cls, kwargs):
		''' 辞書末尾の出現数をcls.wに足す '''
		if not isinstance(kwargs, dict):
			cls.w += kwargs
		else:
			for key in kwargs.keys():
				if isinstance(kwargs[key], dict) and not isinstance(kwargs[key].values(), int):
					cls.__enumkeys(kwargs[key])
				else:
					cls.w += kwargs[key]

	@classmethod
	def __word_choice(cls, sel):
		keys = sel.keys()
		key_w = []
		for key in keys:
			cls.__enumkeys(sel[key])		 # 出現率をcls.wに入れる
			key_w.append(cls.w)			  # key毎に出現率を保管
			cls.w = 0						# cls.wの値を初期化する
		key_w = np.array(key_w) / sum(key_w) # 出現率を平均化して、頻出のものを優先
		choice= np.random.choice(list(keys),p=key_w)
		return choice

class main:

	@staticmethod
	def train():
		markov.dic = {}
		docs = []
		for files in glob(d.docments+'*.tsv'):
			with open(files, encoding='utf-8') as fr:
				for i, l in enumerate(fr):
					l = l.split('\t')
					if l[0] in d.dic_tag and len(l) >= 2:
						markov.dic = json.load(open(d.dict_file.format(l[0]),"r")) if os.path.isfile(d.dict_file.format(l[0])) else {}
						markov.register_dic(l[-1])
						#docs.append(models.doc2vec.TaggedDocument(mecab.mecab_plus(l[-1],True), tags=l[-1]))
						with open(d.dict_file.format(l[0]), 'w') as f:
							json.dump(markov.dic, f, ensure_ascii=False)
		#model = models.doc2vec.Doc2Vec(documents=docs, size=200, window=3, min_count=1, workers=4)
		#model.save(d.doc2_file)

	@staticmethod
	def make(at='@'):
		response = ''
		#model   = models.Word2Vec.load(d.word2_file)
		#while True:
		markov_list  = []
		corpus_list  = mecab.mecab_plus('')
		#docvec	  = model.infer_vector(corpus_list)
		# どの辞書を読み込むか判定する
		for k in d.dic_re:
			if re.search(r'('+d.dic_re[k]+')',''):
				load_dic = k
				break
		markov.dic  = json.load(open(d.dict_file.format(load_dic),"r")) if os.path.isfile(d.dict_file.format(load_dic)) else {}
		# 発言からマルコフ連鎖をいくつか生成
		for co in corpus_list:
			m = markov.make_sentence(co)
			if m : markov_list.append(m)
			#try:
			#	sim = model.most_similar(co, topn = 3)
			#	for s in sim:
			#		if '名詞' in mecab.option(s[0],'-F%f[0]'):
			#			m = markov.make_sentence(s)
			#			if m : markov_list.append(m)
			#except: pass
		if not markov_list:
			response = markov.make_sentence(at)
		else:
			new_response = random.choice(markov_list)
			if new_response == response or mecab.option(new_response,'-F%f[1],').split(',')[0] in ['非自立','格助詞','助詞','接尾','終助詞','連体化']:
				response = markov.make_sentence(at)
			else:
				response = new_response
		return response



def save_tweet(etc=False):
	if etc == False:
		tweets = api.home_timeline(count=10)
	else:
		tweets = api.search_tweets(q=[etc], count=10)
	text = ''
	for tweet in tweets:
		if re.search(r''+re_ng, tweet.text): continue
		text +='twitter\t'+tweet.user.id_str+'\t'+nor(tweet.text)+'\n'
		with open(d.docments+"twitter_corpus.tsv",'a') as f:
			f.write(text)
	'''
	重複した内容を整理
	'''
	text = ''
	with open(d.docments+"twitter_corpus.tsv",'r') as f:
		for line in f:
			text += line

	# 重複を排除するための集合
	s = set()
	
	# ユニークになったデータ（一意になったデータ）
	datas = []
	
	# 処理を開始する
	for src_data in text.split('\n'):
		src_data = src_data.split('\t')
		# もし、タイトル[1]が集合にあったらコンティニューする。
		if src_data[-1] in s:
			continue
	
		# リストに追加して、集合にタイトル[1]を追加する。
		datas.append(src_data)
		s.add(src_data[-1])
	# 使い終わった集合を削除
	del s
	
	text = ''
	for data in datas:
		if len(data) < 3: continue
		text += data[0]+'\t'+data[1]+'\t'+data[2]+'\n'

	with open(d.docments+"twitter_corpus.tsv",'w') as f:
		f.write(text)

def reply_tweet():
	mentions = tweepy.Cursor(api.mentions_timeline, id=API['User']).items(10)
	mention_dict = {}
	mn_users = []
	mn_texts = []
	name = ''
	noreply_id=[]
	for mn in mentions:
		if time_now - (mn.created_at + datetime.timedelta(hours=9)) <= datetime.timedelta(days=check_days):
			with open(d.docments+'noreply_id.txt','r') as f:
				if str(mn.id) in f.read().split('\n'):
					continue
			name = '@'+mn.user.screen_name
			mn_users.append(mn.id)
			mn.text = mn.text.split()[-1]
			m = MeCab.Tagger(d.mecab_dic+' -F%f[1],').parse(mn.text).split(',')[0:-1]
			e = MeCab.Tagger(d.mecab_dic+' -Owakati').parse(mn.text).split()
			_ = dict(zip(m,e))
			v = []
		
			if 'サ変接続' in _:
				save_tweet(_['サ変接続'])
				v.append(_['サ変接続'])
			if '名詞' in _:
				save_tweet(_['名詞'])
				v.append(_['名詞'])
			if v:
				mn_texts.append(name+' '+main.make(random.choice(v)))
			else:
				mn_texts.append(name+' '+main.make('@'))
			mention_dict = dict(zip(mn_users,mn_texts))
	
	for k,v in mention_dict.items():
		try:
			api.update_status(status=v, in_reply_to_status_id=k)
			with open(d.docments+'noreply_id.txt','a') as f:
				f.write(str(k)+'\n')
			print('書き込みました。')
		except:
			pass



if random.randint(1,16) == 16:
	save_tweet()
	main.train()
	api.update_status(main.make())

reply_tweet()
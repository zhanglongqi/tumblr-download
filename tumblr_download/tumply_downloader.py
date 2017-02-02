#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
longqi 1/Feb/17 15:41
Description:


"""
from itertools import count
from multiprocessing.pool import Pool
from os import mkdir
from os.path import basename, join, exists
from pprint import pprint
from urllib.parse import urlparse
from urllib.request import urlretrieve

from .tumblr_api import Tumblpy2


def retrieve_and_save(url, name, path=None):
	filename = join(path, name) if path else name
	if exists(filename):
		return
	print('Downloading: ', url)
	try:
		urlretrieve(url, filename)
	except:
		print('Downloading failed', url)


def get_all_posts(client, blog_url, post_type=None):
	ress = []

	r = client.posts(blog_url, post_type=post_type, limit=1, offset=0)
	print('You have', r['total_posts'], 'video posts')

	ress.append(r)

	for i in count():
		r = client.posts(blog_url, post_type=post_type, limit=50, offset=i * 50)
		ress.append(r)
		if i * 50 > r['total_posts']:
			break
	return ress


downloader_pool = Pool(processes=5)  # use 5 processes to download the data

client = Tumblpy2(
		'zLgPh6LeV7DyczfPALkTEfr8rOgzcYAY8TzAlabVIYrgpATPON',
		'mGP5mVle2ZUNKHzK4ayjAGpfUCkLTmQm91ic9YtWTTcDkdFLPE',
		'hRwAn1CoZJ5Q96T8o51aQL2YcKnh1k66RlnCRLQtqjtWf0WZ4W',
		'oqlple5FP9MVRTxbUQHjrEVSs4DDLFP7h4zBE5D4g952qeqRo3'
)

# Make the request
user_info = client.get('user/info')
print(user_info)
# blog_url = blog_url['user']['blogs'][0]['url']
# print(blog_url)
#
# dashboard = client.get('user/dashboard')
#
# followers= client.get('user/following')
# print(followers)
blog_name = user_info['user']['name']
blog_url = user_info['user']['blogs'][0]['url'][8:-1]
download_list = []

try:
	mkdir(blog_url)
except FileExistsError:
	print('Directory exist', blog_url)
else:
	print('Create dir for blog', blog_url)

for res in get_all_posts(client, blog_url, 'video'):
	for post in res['posts']:
		if 'video_url' in post.keys():
			video_url = post['video_url']
		else:
			continue

		filename = basename(urlparse(video_url).path)

		download_list.append((video_url, filename, blog_url))

pprint(download_list)
output = downloader_pool.starmap(retrieve_and_save, download_list)

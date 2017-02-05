#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
longqi 1/Feb/17 15:41
Description:


"""
import argparse
from itertools import count
from multiprocessing.pool import Pool
from os import mkdir
from os.path import basename, join, exists
from pprint import pprint
from urllib.parse import urlparse
from urllib.request import urlretrieve

from .tumblr_api import Tumblpy2


class TumblrDownload():
	def __init__(self, blog_url, path=None, post_type=None):
		self.downloader_pool = Pool(processes=5)  # use 5 processes to download the data
		self.client = Tumblpy2(
				'zLgPh6LeV7DyczfPALkTEfr8rOgzcYAY8TzAlabVIYrgpATPON',
				'mGP5mVle2ZUNKHzK4ayjAGpfUCkLTmQm91ic9YtWTTcDkdFLPE',
				'hRwAn1CoZJ5Q96T8o51aQL2YcKnh1k66RlnCRLQtqjtWf0WZ4W',
				'oqlple5FP9MVRTxbUQHjrEVSs4DDLFP7h4zBE5D4g952qeqRo3'
		)
		# self.user_info = self.client.get('user/info')
		# self.blog_name = self.user_info['user']['name']
		# self.blog_url = self.user_info['user']['blogs'][0]['url'][8:-1]

		self.blog_url = blog_url
		self.path = path
		self.post_type = post_type

	@staticmethod
	def retrieve_and_save(url, name, path=None):
		filename = join(path, name) if path else name
		if exists(filename):
			return
		print('Downloading: ', url)
		try:
			urlretrieve(url, filename)
		except:
			print('Downloading failed', url)

	def get_all_posts(self, client, blog_url, post_type=None):
		ress = []

		r = client.posts(blog_url, post_type=post_type, limit=1, offset=0)
		print('You have', r['total_posts'], self.post_type, ' posts')

		ress.append(r)

		for i in count():
			r = client.posts(blog_url, post_type=post_type, limit=50, offset=i * 50)
			ress.append(r)
			if i * 50 > r['total_posts']:
				break
		return ress

	def to_download(self):
		download_list = []
		try:
			mkdir(self.blog_url)
		except FileExistsError:
			print('Directory exist', self.blog_url)
		else:
			print('Create dir for blog', self.blog_url)

		for res in self.get_all_posts(self.client, self.blog_url, self.post_type):
			for post in res['posts']:
				if post['type'] == 'video':
					url = post['video_url']
				# todo support all the post types
				else:
					continue

				filename = basename(urlparse(url).path)
				download_list.append((url, filename, self.blog_url))

		pprint(download_list)
		self.downloader_pool.starmap(self.retrieve_and_save, download_list)


# blog_url = blog_url['user']['blogs'][0]['url']
# print(blog_url)
#
# dashboard = client.get('user/dashboard')
#
# followers= client.get('user/following')
# print(followers)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()

	parser.add_argument('blog')
	parser.add_argument('--type', '-t', action='store',
											help='The posts type you want to download:'
													 'Text,Photo,Quote,Link,Chat, Audio, Video,Answer')
	parser.add_argument('--path', '-p', action='store',
											help='The directory that store all the files you download.')
	args = parser.parse_args()
	if str.lower(str(args.type)) not in ['text', 'photo', 'quote', 'link', 'chat', 'audio', 'video', 'answer']:
		print('You can only select type in Text, Photo, Quote, Link, Chat, Audio, Video, Answer')
		exit(1)
	loader = TumblrDownload(args.blog, path=args.path, post_type=args.type)
	loader.to_download()

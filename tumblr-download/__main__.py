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
from urllib.parse import urlparse
from urllib.request import urlretrieve
from bs4 import BeautifulSoup

from tumblr_api import Tumblpy2


class TumblrDownload:
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
	def retrieve_and_save(d):
		url = d.get('url', '')
		filename = d.get('filename', '')
		path = d.get('path', None)

		filename = join(path, filename) if path else filename
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
		print(blog_url, 'have', r['total_posts'], self.post_type, 'posts')

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
				if post['type'] == 'video' and 'tumblr' == post['video_type']:
					url = post.get('video_url', '')
					if url:
						download_list.append({'url'     : url,
																	'filename': basename(urlparse(url).path),
																	'path'    : self.blog_url})
					else:
						print('Can not download this post:', post['post_url'])
				elif post['type'] == 'photo':
					for photo in post.get('photos', []):
						url = photo.get('original_size', {}).get('url', '')
						if url:
							download_list.append({'url'     : url,
																		'filename': basename(urlparse(url).path),
																		'path'    : self.blog_url})
						else:
							print('Can not download this post:', post['post_url'])
				elif post['type'] == 'audio':
					pass
				elif post['type'] == 'text':
					body = post.get('body', '')
					soup = BeautifulSoup(body, 'html.parser')
					for img in soup.find_all('img'):
						url = img.get('src', '')
						if url:
							download_list.append({'url'     : url,
																		'filename': basename(urlparse(url).path),
																		'path'    : self.blog_url})
				else:
					continue

		# pprint(download_list)
		self.downloader_pool.map(self.retrieve_and_save, download_list)


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
													 'Text, Photo, Quote, Link, Chat, Audio, Video, Answer')
	parser.add_argument('--path', '-p', action='store',
											help='The directory that store all the files you download.')
	args = parser.parse_args()
	if str.lower(str(args.type)) not in ['text', 'photo', 'quote', 'link', 'chat', 'audio', 'video', 'answer']:
		print('You have to select one type, such as Text, Photo, Quote, Link, Chat, Audio, Video, Answer')
		exit(1)
	loader = TumblrDownload(args.blog, path=args.path, post_type=args.type)
	loader.to_download()

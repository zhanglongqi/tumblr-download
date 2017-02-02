#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
longqi 20/Apr/16 13:33
Description:


"""

from tumblpy import Tumblpy


class Tumblpy2(Tumblpy):
	def __init__(self, app_key=None, app_secret=None, oauth_token=None,
							 oauth_token_secret=None, headers=None, proxies=None):
		Tumblpy.__init__(self, app_key, app_secret, oauth_token,
										 oauth_token_secret, headers, proxies)

	def posts(self, blogname, post_type=None, **kwargs):
		"""
		Gets the posts that BLOG_URL.
		:param limit: an int, the number of likes you want returned
		:param offset: an int, the blog you want to start at, for pagination.

				# Start at the 20th post and get 20 more posts.
				client.posts({'offset': 20, 'limit': 20})

		:returns: A dict created from the JSON response
		"""
		if post_type is None:
			url = 'blog/%s/posts' % blogname
		else:
			url = 'blog/%s/posts/%s' % (blogname, post_type)
		return self.get(url, params=kwargs)

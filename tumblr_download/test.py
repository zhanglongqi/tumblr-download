#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
longqi 20/Apr/16 13:33
Description:


"""

from sqlalchemy import Column, Float, String, Integer
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

Base = declarative_base()


class Resource(Base):
    __tablename__ = 'tumblr'
    # Here we define columns for the table address.
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer(), primary_key=True)
    resource_name = Column(String(250))
    time_stamp = Column(Float())


# Create an engine that stores data in the local directory's
engine = create_engine('sqlite:///tumblr.db')

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

################


from tumblpy import Tumblpy
from time import time

# Authenticate via OAuth
client = Tumblpy(
    'zLgPh6LeV7DyczfPALkTEfr8rOgzcYAY8TzAlabVIYrgpATPON',
    'mGP5mVle2ZUNKHzK4ayjAGpfUCkLTmQm91ic9YtWTTcDkdFLPE',
    'hRwAn1CoZJ5Q96T8o51aQL2YcKnh1k66RlnCRLQtqjtWf0WZ4W',
    'oqlple5FP9MVRTxbUQHjrEVSs4DDLFP7h4zBE5D4g952qeqRo3'
)

dashboard = client.dashboard()

for post in dashboard['posts']:
    resource_urls = []
    # resource_names = []

    if post['type'] == 'photo':
        for photo in post['photos']:
            resource_urls.append(photo['original_size']['url'])
            # resource_names.append(photo['original_size']['url'].rsplit('/', 1)[-1])
    elif post['type'] == 'video':
        resource_urls.append(post['video_url'])
        # resource_names.append(post['video_url'].rsplit('/', 1)[-1])
    else:
        continue

    # print(resource_urls)
    to_downloads = []
    for resource_url in resource_urls:
        resource_name = resource_url.rsplit('/', 1)[-1]
        try:
            session.query(Resource).filter(Resource.resource_name == resource_name).one()
        except NoResultFound:
            to_downloads.append(resource_url)
            new_resource_item = Resource(resource_name=resource_name, time_stamp=time())
            session.add(new_resource_item)
        else:
            continue
    session.commit()

    import subprocess

    for to_download in to_downloads:
        print(type(to_download), to_download)

        subprocess.call(['youtube-dl', to_download])

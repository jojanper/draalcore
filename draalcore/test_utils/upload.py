#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""File upload utility"""

# System imports
import os


TEST_FILE_IMAGE = os.path.join(os.path.dirname(__file__), 'pic.jpg')
TEST_FILE_CONTENT_HEADER = 'attachment; filename="pic.jpg"'
TEST_FILE_INVALID = os.path.join(os.path.dirname(__file__), 'test.invalid')
TEST_FILE_GIF = os.path.join(os.path.dirname(__file__), 'pic.gif')
TEST_FILE_MP3 = os.path.join(os.path.dirname(__file__), 'audio.mp3')
TEST_FILE_MP4 = os.path.join(os.path.dirname(__file__), 'video.mp4')


def upload_file(api, method='test_upload1', with_file=True, test_file='test1', **kwargs):
    if test_file == 'test1':
        upload_file = TEST_FILE_IMAGE
    elif test_file == 'test3':
        upload_file = TEST_FILE_GIF
    elif test_file == 'audio':
        upload_file = TEST_FILE_MP3
    elif test_file == 'video':
        upload_file = TEST_FILE_MP4
    else:
        upload_file = TEST_FILE_INVALID

    with open(upload_file, 'rb') as fp:
        attachment = {"name": "test upload"}
        if with_file:
            attachment['file'] = fp

        return getattr(api, method)(attachment, **kwargs)

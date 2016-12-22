#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import connection


class SqldumpMiddleware(object):
    def process_response(self, request, response):
        if settings.DEBUG and 'sqldump' in request.GET:
            sqlList = list()
            for item in connection.queries:
                sqlList.append(str(item))
            response.content = str('\n'.join(sqlList))
            response['Content-Type'] = 'text/plain'
        return response

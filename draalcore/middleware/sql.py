#!/usr/bin/env python
# -*- coding: utf-8 -*-

# System imports
from django.conf import settings
from django.db import connection

# Project imports
from draalcore.middleware.base import BaseMiddleware


class SqldumpMiddleware(BaseMiddleware):
    """
    Return raw SQL queries executed for HTTP GET request. Useful for
    quickly debugging SQL queries. 'sqldump' query parameter must be
    present in the HTTP GET request. For more advanced SQL debugging,
    Django debug toolbar is recommended.
    """

    def process_response(self, request, response):
        if settings.DEBUG and 'sqldump' in request.GET:
            sqlList = list()
            for item in connection.queries:
                sqlList.append(str(item))
            response.content = str('\n'.join(sqlList))
            response['Content-Type'] = 'text/plain'
        return response

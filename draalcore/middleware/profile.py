# Copyright (C) 2011 by Blade Polska s.c.
# Full rights belong to Tomek Kopczuk (@tkopczuk).
# www.askthepony.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from datetime import datetime
import cProfile
import os
import StringIO
import pstats
import marshal
from django.core.exceptions import MiddlewareNotUsed
from django.conf import settings
import subprocess
import tempfile

from django.http import HttpResponse
from django.shortcuts import redirect
from django.test.client import Client

import hotshot

import time


class InstrumentMiddleware(object):
    def process_request(self, request):
        try:
            params = getattr(request, request.method)
        except AttributeError:
            params = getattr(request, 'POST')

        if 'profile' in params:
            request.profiler = cProfile.Profile()
            request.profiler.enable()

    def process_response(self, request, response):
        if hasattr(request, 'profiler'):
            request.profiler.disable()
            stamp = (request.META['REMOTE_ADDR'], datetime.now())
            request.profiler.dump_stats('/tmp/%s-%s.pro' % stamp)

            stream = StringIO.StringIO()
            stats = pstats.Stats('/tmp/%s-%s.pro' % stamp, stream=stream)
            stats.strip_dirs()
            stats.sort_stats('time')
            stats.print_stats(12)
            stats.print_callers(12)
            stats.print_callees(12)
            os.remove('/tmp/%s-%s.pro' % stamp)
            response._container[0] += '<pre style="color: #FFF">'+stream.getvalue()+'</pre>'
            stream.close()
        return response


class ProfileMiddleware(object):
    def __init__(self):
        if not settings.DEBUG:
            raise MiddlewareNotUsed()
        self.profiler = None

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if settings.DEBUG and ('profiler' in request.GET or 'profilerbin' in request.GET):
            self.profiler = cProfile.Profile()
            args = (request,) + callback_args
            return self.profiler.runcall(callback, *args, **callback_kwargs)

    def process_response(self, request, response):
        if settings.DEBUG:
            if 'profiler' in request.GET:
                self.profiler.create_stats()
                out = StringIO.StringIO()
                stats = pstats.Stats(self.profiler, stream=out)
                # Values for stats.sort_stats():
                # - calls           call count
                # - cumulative      cumulative time
                # - file            file name
                # - module          file name
                # - pcalls          primitive call count
                # - line            line number
                # - name            function name
                # - nfl                     name/file/line
                # - stdname         standard name
                # - time            internal time
                stats.sort_stats('time').print_stats(.2)
                response.content = out.getvalue()
                response['Content-type'] = 'text/plain'
                return response
            if 'profilerbin' in request.GET:
                self.profiler.create_stats()
                response.content = marshal.dumps(self.profiler.stats)
                filename = request.path.strip('/').replace('/', '_') + '.pstat'
                response['Content-Disposition'] = \
                    'attachment; filename=%s' % (filename,)
                response['Content-type'] = 'application/octet-stream'
                return response
        return response


"""A Django middleware for interactive profiling"""

OUT_FORMAT = 'png'
GPROF2PY_PATH = '/home/jojanper/work/python_snippets/profiling'

__all__ = ['VisorMiddleware']


class HolodeckException(Exception):
    """Captain, the holodeck's malfunctioning again!"""


class HoloRequest(object):
    """A simulated, test client request that Celery can pickle.

    This tries to copy everything off of a real request object in order to
    replay it with the Django test client.
    """

    def __init__(self, request):
        """Initialize a HoloRequest.

        request should be a Django request object.
        """
        self._method = request.method
        self._headers = dict([(k, v) for (k, v) in request.META.iteritems()
                              if k.startswith('HTTP_')])
        # XXX: Handle raw POST bodies
        self._data = dict((k, request.POST[k]) for k in request.POST)

        path = request.path
        query = request.GET.copy()
        query.pop('__geordi__', None)
        query = query.urlencode()
        if query:
            path += '?' + query
        self._path = path

    def profile(self, options=''):
        """Profile the request and return a PDF/PNG/JPG/etc of the call graph"""
        client = Client()
        callback = {'GET': client.get,
                    'POST': client.post,
                    'HEAD': client.head,
                    'OPTIONS': client.options,
                    'PUT': client.put,
                    'DELETE': client.delete}[self._method]

        profiler = cProfile.Profile()
        profiler.runcall(callback, self._path, self._data, **self._headers)
        profiler.create_stats()

        with tempfile.NamedTemporaryFile() as stats:
            stats.write(marshal.dumps(profiler.stats))
            stats.flush()
            # XXX: Formatting a shell string like this isn't ideal.
            cmd = ('%s/gprof2dot.py %s -f pstats %s | dot -T%s'
                   % (GPROF2PY_PATH, options, stats.name, OUT_FORMAT))
            proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE)
            output = proc.communicate()[0]
            retcode = proc.poll()
            if retcode:
                raise HolodeckException('gprof2dot/dot exited with %d'
                                        % retcode)
        return output


if getattr(settings, 'GEORDI_CELERY', False):
    from celery.task import task

    @task
    def profiletask(srequest, options):
        """Profile a request in a background Celery task"""
        outputdir = getattr(settings, 'GEORDI_OUTPUT_DIR', None)
        with tempfile.NamedTemporaryFile(prefix='geordi-', suffix='.' + OUT_FORMAT,
                                         dir=outputdir,
                                         delete=False) as outfile:
            outfile.write(srequest.profile(options))
            return outfile.name
else:
    profiletask = None


class VisorMiddleware(object):
    """Interactive profiling middleware.

    When a request comes in that has a __geordi__ GET parameter, this bypasses
    the view function, profiles the request, and returns the profiler output.

    Note that this only runs if settings.DEBUG is True or if the current user
    is a super user.
    """

    _refresh = """<!DOCTYPE html>
<head>
<title>Profiling...</title>
<meta http-equiv=refresh content=3>
</head>
<body>
<p>Profiling...</p>
"""

    def _allowed(self, request):
        """Return whether or not the middleware should run"""
        if settings.DEBUG:
            return True
        user = getattr(request, 'user', None)
        if user is not None:
            return user.is_superuser
        else:
            return False

    def _profile(self, task_id, request):
        """Profile the request asynchronously"""
        if task_id == '':
            options = getattr(settings, 'GEORDI_GPROF2DOT_OPTIONS', '')
            srequest = HoloRequest(request)
            result = profiletask.delay(srequest, options)

            query = request.GET.copy()
            query['__geordi__'] = result.task_id
            return redirect(request.path + '?' + query.urlencode())
        else:
            result = profiletask.AsyncResult(task_id)
            if not result.ready():
                return HttpResponse(self._refresh)
            else:
                with open(result.get(), 'rb') as outfile:
                    output = outfile.read()
                return HttpResponse(output, content_type='application/' + OUT_FORMAT)

    def _profilenow(self, request):
        """Profile the request in-process"""
        options = getattr(settings, 'GEORDI_GPROF2DOT_OPTIONS', '')
        srequest = HoloRequest(request)
        return HttpResponse(srequest.profile(options),
                            content_type='application/' + OUT_FORMAT)

    def process_view(self, request, *args, **kwargs):
        """Handle view bypassing/profiling"""
        if not self._allowed(request):
            return

        task_id = request.GET.get('__geordi__', None)
        if task_id is None:
            return

        if profiletask:
            return self._profile(task_id, request)
        else:
            return self._profilenow(request)


PROFILE_LOG_BASE = os.path.dirname(os.path.abspath(__file__))


def profile(log_file):
    """Profile some callable.

    This decorator uses the hotshot profiler to profile some callable (like
    a view function or method) and dumps the profile data somewhere sensible
    for later processing and examination.

    It takes one argument, the profile log name. If it's a relative path, it
    places it under the PROFILE_LOG_BASE. It also inserts a time stamp into the
    file name, such that 'my_view.prof' become 'my_view-20100211T170321.prof',
    where the time stamp is in UTC. This makes it easy to run and compare
    multiple trials.
    """

    if not os.path.isabs(log_file):
        log_file = os.path.join(PROFILE_LOG_BASE, log_file)

    def _outer(f):
        def _inner(*args, **kwargs):
            # Add a timestamp to the profile output when the callable
            # is actually called.
            (base, ext) = os.path.splitext(log_file)
            base = base + "-" + time.strftime("%Y%m%dT%H%M%S", time.gmtime())
            final_log_file = base + ext

            prof = hotshot.Profile(final_log_file)
            try:
                ret = prof.runcall(f, *args, **kwargs)
            finally:
                prof.close()
            return ret

        return _inner
    return _outer

#!/usr/bin/env python
"""
Reads an http log file from standard input and splits
by http 1.1 host.

Format of the log file should be:

hostname standard_combined_format_entry[ sent_http_content_type]?

Split logs are output into current directory, and will overwrite
existing files.

A Zope/Plone adaptation: if sent_http_content_type is present, and
is "text|image/something...", the MIME subtype will be added to the
request URL before the #|? (if any). This will help log analysis
programs identify doc types that may otherwise be anonymous.

Output is combined format, so both hostname and content type are
stripped.
"""

import re
import sys

# nginx log format:
#
# log_format custom   '$host $remote_addr - $remote_user [$time_local] '
#                     '"$request" $status $body_bytes_sent '
#                     '"$http_referer" "$http_user_agent" "$sent_http_content_type"'

# re to split log lines
log_re = re.compile(r'^(.+?) (.+?) - (.+?) \[(.*?)\] ' \
    r'"(.+) (.*?)" (.+?) (.+?) ' \
    r'"(.*?)" "(.*?)"(?: "(.+?)")?$')

# here's how we'll write it out
output_format = \
    '%(remote_addr)s - %(remote_user)s [%(time_local)s] ' \
    '"%(request)s %(protocol)s" %(status)s %(body_bytes_sent)s ' \
    '"%(http_referer)s" "%(http_user_agent)s"'

# re to check hostname
okfile_re = re.compile(r"^[a-z0-9_\-.]+$")

# subtype identification
subtype_re = re.compile(r"^(?:text|image)/(.+);?.*$")
# url splitter re
ext_re = re.compile(r"^([^#?]+)(.*)$")

out_files = {}
for line in sys.stdin:
    rez = log_re.findall(line)
    if rez:
        (host, remote_addr, remote_user, time_local, \
        request, protocol, status, body_bytes_sent, \
        http_referer, http_user_agent, \
        content_type) = rez[0]

        rez = subtype_re.findall(content_type)
        if rez:
            main, query = ext_re.findall(request)[0]
            if main[-1] == '/':
                main = main[:-1]
            if main:
                ext = '.' + rez[0]
                ext = ext.replace('x-', '')
                ext = ext.replace('javascript', 'js')
                ext = ext.replace('jpeg', 'jpg')
                if not main.endswith(ext):
                    request = "%s%s%s" % (main, ext, query)

        rdict = {
            'host': host,
            'remote_addr': remote_addr,
            'remote_user': remote_user,
            'time_local': time_local,
            'request': request,
            'protocol': protocol,
            'status': status,
            'body_bytes_sent': body_bytes_sent,
            'http_referer': http_referer,
            'http_user_agent': http_user_agent,
            'sent_http_content_type': content_type,
        }
        if host.startswith('www.'):
            host = host[4:]
        if not okfile_re.match(host):
            print "Bad host %s" % host
            continue
        out = out_files.get(host, None)
        if out is None:
            out = open(host, 'w', 32 * 1024)
            out_files[host] = out
        print >> out, output_format % rdict

for afile in out_files.values():
    afile.close()

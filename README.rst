logsplit
========

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
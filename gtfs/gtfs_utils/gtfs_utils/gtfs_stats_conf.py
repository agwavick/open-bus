import re

OUTPUT_FILE_NAME_RE = re.compile('^(?P<date_str>[^_]+?)'
                                 '_(?P<type>\w+)\.pkl\.gz')

BUCKET_VALID_FILES_RE = re.compile('2019-\d\d-\d\d\.zip')
#BUCKET_VALID_FILES_RE = re.compile('2019-03-12.zip')

STATS_TYPES = ['trip_stats', 'route_stats']

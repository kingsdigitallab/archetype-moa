# Source Generated with Decompyle++
# File: local_settings.pyc (Python 2.7)

import os
DEBUG = True

ADMINS = []
SERVER_EMAIL = 'no-reply@kcl.ac.uk'
EMAIL_SUBJECT_PREFIX = '[mofa-liv] '
MANAGERS = ADMINS

ALLOWED_HOSTS = [
    '142.93.41.124',
    'localhost',
    '.mofa.dighum.kcl.ac.uk',
    '.moa.cch.kcl.ac.uk',
    '.modelsofauthority.ac.uk'
]

SITEMAP_PATH_TO_RESOURCE = 'http://www.modelsofauthority.ac.uk/'

SHOW_QUICK_SEARCH_SCOPES = True

LIGHTBOX = True

SITE_TITLE = 'Models of Authority'

TWITTER = 'modelsauthority'
#COMMENTS_DISQUS_SHORTNAME = 'yourDisqusName'

REJECT_HTTP_API_REQUESTS = True
ANNOTATOR_ZOOM_LEVELS = 7

# customisations of the faceted search
from customisations.digipal.views.faceted_search.settings import FACETED_SEARCH 

FOOTER_LOGO_LINE = True

HAND_DEFAULT_LABEL = 'Main Hand'
HAND_ID_PREFIX = 'MoA Hand '

MODELS_PUBLIC = ['itempart', 'image', 'graph', 'textcontentxml', 'hand', 'scribe', 'clause', 'title']
MODELS_PRIVATE = ['itempart', 'image', 'graph', 'textcontentxml', 'hand', 'scribe', 'clause', 'title']

AUTOCOMPLETE_PUBLIC_USER = True

PAGE_IMAGE_SHOW_MSDATE = True
PAGE_IMAGE_SHOW_MSSUMMARY = True

GRAPH_TOOLTIP_SHORT = u'{allograph}\n{desc}'
GRAPH_TOOLTIP_LONG = u'Allograph: {allograph}\n {ip}\n ({hi_date})\n{desc}'

MIN_THUMB_LENGTH = 100
MAX_THUMB_LENGTH = 500

KDL_MAINTAINED = True

API_PERMISSIONS = [['r', 'ALL'], ['', 'user']]

# dirty trick: code still imports from mofa package
# but with docker everything is under digipal_project

if not os.path.exists('mofa'):
    os.system('ln -s digipal_project mofa')

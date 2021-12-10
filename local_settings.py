# Source Generated with Decompyle++
# File: local_settings.pyc (Python 2.7)

import os


def get_env(name, default=None):
    return os.environ.get(name, default)


DEBUG = get_env('DJANGO_DEBUG', 'False') == 'True'
image_server_host = get_env('IMAGE_SERVER_HOST')

ADMINS = []
SERVER_EMAIL = 'no-reply@kcl.ac.uk'
EMAIL_SUBJECT_PREFIX = '[mofa-liv] '
MANAGERS = ADMINS

if image_server_host:
    # 'mofa-images.dighum.kcl.ac.uk'
    IMAGE_SERVER_HOST = image_server_host
    IMAGE_SERVER_ZOOMIFY = 'https://%s%s?zoomify=%s/'
    IMAGE_SERVER_PATH = '/iip/iipsrv.fcgi'
    IMAGE_SERVER_URL = 'https://%s%s' % (IMAGE_SERVER_HOST, IMAGE_SERVER_PATH)
    IMAGE_URLS_RELATIVE = False

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

MODELS_PRIVATE = ['itempart', 'image', 'graph', 'textcontentxml', 'handdescription', 'scribe', 'clause', 'person']
MODELS_PUBLIC = MODELS_PRIVATE

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

ARCHETYPE_SEARCH_HELP_URL = '/about/search/'

# These are urls for class-based generic views.
from django.conf.urls.defaults import *
from parse_tweet.views import *

urlpatterns = patterns('core.views',
    # Mobile versions
    url(r'^m/parser/$', ParserView.as_view(template_name='mobile/parser.html'), name='mobile-parser'),
    # Desktop versions
    url(r'^parser/$', ParserView.as_view(), name='parser'),
)

# These are urls for class-based generic views.
from django.conf.urls.defaults import *
from core.views import *

urlpatterns = patterns('core.views',
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^edit/$', EditView.as_view(), name='edit'),
    url(r'^(?P<road>[a-zA-Z0-9\-]+)/$', RoadView.as_view(), name='show_road'),
)

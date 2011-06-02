# These are urls for class-based generic views.
from django.conf.urls.defaults import *
from core.views import *

urlpatterns = patterns('core.views',
    # Mobile versions
    url(r'^m/$', HomeView.as_view(template_name='mobile/home.html'), name='mobile-home'),
    url(r'^m/(?P<road>[a-zA-Z0-9\-]+)/$', RoadView.as_view(template_name='mobile/road.html'), name='mobile-show_road'),
    url(r'^m/(?P<road>[a-zA-Z0-9\-]+)/edit/$', EditRoad.as_view(template_name='mobile/edit.html'), name='mobile-edit_road'),
    # Desktop versions
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^grid/$', TemplateView.as_view(template_name='grid.html'), name='grid'),
    url(r'^grid/sections/$', GenerateSections.as_view(), name='generate_sections'),
    url(r'^(?P<road>[a-zA-Z0-9\-]+)/$', RoadView.as_view(), name='show_road'),
    url(r'^(?P<road>[a-zA-Z0-9\-]+)/edit/$', EditRoad.as_view(), name='edit_road'),
)

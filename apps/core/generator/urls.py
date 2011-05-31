# These are urls for class-based generic views.
from django.conf.urls.defaults import *
from core.generator.views import *

urlpatterns = patterns('core.generator.views',

    url(r'^node/new/$', NodeCreateView.as_view(), name='node_new'),
    url(r'^node/$', NodeListView.as_view(), name='node_list'),
    url(r'^node/show/(?P<pk>[\d]+)/$', NodeDetailView.as_view(), name='node_show'),
    url(r'^node/edit/(?P<pk>[\d]+)/$', NodeUpdateView.as_view(), name='node_edit'),
    url(r'^node/delete/(?P<pk>[\d]+)/$', NodeDeleteView.as_view(), name='node_delete'),

    url(r'^road/new/$', RoadCreateView.as_view(), name='road_new'),
    url(r'^road/$', RoadListView.as_view(), name='road_list'),
    url(r'^road/show/(?P<pk>[\d]+)/$', RoadDetailView.as_view(), name='road_show'),
    url(r'^road/edit/(?P<pk>[\d]+)/$', RoadUpdateView.as_view(), name='road_edit'),
    url(r'^road/delete/(?P<pk>[\d]+)/$', RoadDeleteView.as_view(), name='road_delete'),

    url(r'^section/new/$', SectionCreateView.as_view(), name='section_new'),
    url(r'^section/$', SectionListView.as_view(), name='section_list'),
    url(r'^section/show/(?P<pk>[\d]+)/$', SectionDetailView.as_view(), name='section_show'),
    url(r'^section/edit/(?P<pk>[\d]+)/$', SectionUpdateView.as_view(), name='section_edit'),
    url(r'^section/delete/(?P<pk>[\d]+)/$', SectionDeleteView.as_view(), name='section_delete'),

    url(r'^situation/new/$', SituationCreateView.as_view(), name='situation_new'),
    url(r'^situation/$', SituationListView.as_view(), name='situation_list'),
    url(r'^situation/show/(?P<pk>[\d]+)/$', SituationDetailView.as_view(), name='situation_show'),
    url(r'^situation/edit/(?P<pk>[\d]+)/$', SituationUpdateView.as_view(), name='situation_edit'),
    url(r'^situation/delete/(?P<pk>[\d]+)/$', SituationDeleteView.as_view(), name='situation_delete'),

    url(r'^user/new/$', UserCreateView.as_view(), name='user_new'),
    url(r'^user/$', UserListView.as_view(), name='user_list'),
    url(r'^user/show/(?P<pk>[\d]+)/$', UserDetailView.as_view(), name='user_show'),
    url(r'^user/edit/(?P<pk>[\d]+)/$', UserUpdateView.as_view(), name='user_edit'),
    url(r'^user/delete/(?P<pk>[\d]+)/$', UserDeleteView.as_view(), name='user_delete'),

)

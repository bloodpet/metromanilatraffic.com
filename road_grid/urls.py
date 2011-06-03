from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'road_grid.views.home', name='home'),
    # url(r'^road_grid/', include('road_grid.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    url(r'^m/login/$', 'accounts.views.login', {'template_name': 'mobile/signin.html'}, name='mobile-accounts-login'),

    url(r'^accounts/', include('accounts.urls')),
    url(r'^road_grid/', include('core.generator.urls')),
    url(r'^', include('core.urls')),
)

try:
    from local_urls import *
except ImportError:
    pass

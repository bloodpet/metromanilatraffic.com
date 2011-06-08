from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm, password_change, password_change_done
import views as toplevel
#import fbconnect, twitter

urlpatterns = patterns(
    '',
    url(r'^edit/$', toplevel.edit, name='accounts-edit'),
    #url(r'^fbconnect/authenticate/$', fbconnect.authenticate, name='accounts-fbconnect-authenticate'),
    #url(r'^fbconnect/xd_receiver.htm$', fbconnect.xd_receiver, name='accounts-fbconnect-xd_receiver'),
    #url(r'^twitter/authenticate/$', twitter.authenticate, name='accounts-twitter-authenticate'),
    #url(r'^twitter/callback/$', twitter.process_callback, name='accounts-twitter-callback'),
    url(r'^logout/$', toplevel.logout, name='accounts-logout'),
    url(r'^login/$', toplevel.login, name='accounts-login'),
    url(r'^password/change/done/$', password_change_done, {'template_name': 'accounts/password_change_done.html'},name="password-change-done"),
    url(r'^password/change/$', password_change,{'template_name': 'accounts/password_change.html'},name="password-change"),
    url(r'^password/reset/done/$', password_reset_done, {'template_name': 'accounts/password_reset_done.html'},name="password-reset-done"),
    url(r'^password/reset/$', password_reset,{'template_name': 'accounts/password_reset.html','email_template_name':'accounts/password_reset_email.html'},name="password-reset"),
    url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)$',password_reset_confirm,{'template_name':'accounts/password_reset_confirm.html'},name="password-reset-confirm"),
    url(r'^password/reset/complete/$','django.contrib.auth.views.password_reset_complete',{'template_name':'accounts/password_reset_complete.html'}),
    url(r'^postauthcmd/$', toplevel.postauthcmd, name='accounts-postauthcmd'),
    url(r'^$', toplevel.index, name='accounts-index'),
    url(r'^details/(?P<userid>\d+)/$', toplevel.user_details, name='accounts-details'),
    url(r'^confirm-email/(?P<useridb36>[0-9A-Za-z]+)-(?P<token>.+)/$', toplevel.user_confirm_email, name='accounts-user-confirm-email'),
)

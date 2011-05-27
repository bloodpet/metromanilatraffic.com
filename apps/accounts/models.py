from django.conf import settings
from django.contrib.auth.models import User,Group
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.db import models
from django.db.models import signals
from django.template import Context, loader
from django.utils.http import int_to_base36
from django.utils.translation import ugettext, ugettext_lazy as _

import sys

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    twitter_id = models.CharField(max_length=15, blank=True, null=True)
    twitter_access_token = models.TextField(blank=True, null=True, editable=False)
    facebook_id = models.PositiveIntegerField(blank=True, null=True)
    facebook_name = models.CharField(max_length=128, blank=True, null=True)
    email_confirmed = models.BooleanField(default=False)
    third_party_picture = models.URLField(verify_exists=False,blank=True,null=True)

    def __init__(self, *args, **kwargs):
        super(UserProfile, self).__init__(*args, **kwargs)
        self.twitter_api = None

    def get_display_name(self):
        if self.twitter_id:
            return u'@%s' % self.twitter_id
        elif self.facebook_id:
            if self.facebook_name:
                return u'%s' % self.facebook_name
            else:
                return u'%sFacebook User %d' % self.facebook_id
        else:
            if self.user.first_name and self.user.last_name:
                return self.user.get_full_name()
            else:
                return self.user.username
    def switch_user_type(self):
        """
        for development for easily switch user
        """
        self.user.groups.all().delete()
        user_type = self.get_user_type()
        if user_type == 'performer':
            self.user.groups.add(Group.objects.get_or_create(name="Clients")[0])
        else:
            self.user.groups.add(Group.objects.get_or_create(name="Performers")[0])

    def get_user_type(self):
        """
        get user type
        whether
        'performers'
        or 
        'clients'
        if user doesn't have those both group, the default is clients.
        """
        clients_groups = self.user.groups.filter(name='Clients')
        if clients_groups.count() > 0:
            return 'Clients'
        
        performers_groups = self.user.groups.filter(name='Performers')
        if performers_groups.count() > 0:
            return 'Performers'
        
        return 'Clients'

    def get_twitter_api(self):
        if self.twitter_id is None or 0 == len(self.twitter_id):
            return None

        if self.twitter_api is None:
            import cgi
            import tweepy

            try:
                self.twitter_api = tweepy.API.new('oauth', settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
                access_token_params = cgi.parse_qs(self.twitter_access_token, keep_blank_values=False)
                key = access_token_params['oauth_token'][0]
                secret = access_token_params['oauth_token_secret'][0]
                self.twitter_api.auth_handler.set_access_token(key, secret)
            except tweepy.TweepError, e:
                return None

        return self.twitter_api

def create_userprofile(sender, **kwargs):
    created = kwargs['created']
    user = kwargs['instance']

    if created:
        userprofile = UserProfile(user=user)
        userprofile.save()

def send_confirmation_email(user):
    current_site = Site.objects.get_current()
    email_context = dict(
        email=user.email,
        site_name=current_site.name,
        domain=current_site.domain,
        useridb36=int_to_base36(user.pk),
        token=token_generator.make_token(user),
        protocol='http'
    )
    email_template = getattr(settings, 'ACCOUNTS_EMAIL_CONFIRMATION_TEMPLATE', 'accounts/email_confirmation.txt')
    t = loader.get_template(email_template)

    if settings.DEBUG:
        print >>sys.stderr, t.render(Context(email_context)).strip()
    else:
        send_mail(
            _(u'Email Address Confirmation Request from %s') % current_site.name,
            t.render(Context(email_context)).strip(),
            settings.SERVER_EMAIL,
            (user.email,),
        )

signals.post_save.connect(create_userprofile, User)

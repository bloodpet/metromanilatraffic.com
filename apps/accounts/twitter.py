from django.conf import settings
from django.core.urlresolvers import reverse as url_for_view
from django.contrib.auth.models import User
from django.db import transaction
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from models import UserProfile

import accounts, tweepy, utils

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()

class TwitterAuthenticationBackend(object):
    def authenticate(self, **credentials):
        access_token = credentials.get('token')
        request = credentials.get('request')
        if access_token is None:
            return None

        auth = tweepy.OAuthHandler(
            settings.TWITTER_CONSUMER_KEY,
            settings.TWITTER_CONSUMER_SECRET
        )
        auth.access_token = access_token
        api = tweepy.API(auth)
        if not api.verify_credentials():
            return None
        else:
            credentials = api.me()

        username = 'twit_%s' % (str(credentials.id))
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Check to see if there is already a UserProfile with a matching
            # screen_name. This is so that we can allow users to change their
            # default Django auth usernames.
            try:
                profile = UserProfile.objects.get(twitter_id=credentials.screen_name)
            except UserProfile.DoesNotExist:
                user = User(username=username)
                user.save()
                user.set_password(utils.get_random_password())
                profile = user.get_profile()
                profile.twitter_id = credentials.screen_name
                profile.twitter_access_token = unicode(auth.access_token)
                profile.save()
                request.session['is_new_user_account'] = True
            else:
                user = profile.user
                if profile.twitter_access_token != auth.access_token:
                    profile.twitter_access_token = unicode(auth.access_token)
                    profile.save()
        else:
            profile = user.get_profile()
            if profile.twitter_access_token != auth.access_token:
                # We have a new access token. Update the one we have
                # stored for this user.
                profile.twitter_access_token = unicode(auth.access_token)
                profile.save()

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

def authenticate(request):
    '''
    Performs the redirect to authenticate with Twitter.

    * URL Name

      ``accounts-twitter-authenticate``

    * Available Context

      ``twitter_error_message`` - Set only when Twitter authentication results in an exception.

    * Template

      'accounts/twitter_error.html' - Used only when Twitter authentication results in an exception. Otherwise none.

    '''
    auth = tweepy.OAuthHandler(
        settings.TWITTER_CONSUMER_KEY,
        settings.TWITTER_CONSUMER_SECRET,
        settings.BASE_URL + url_for_view('accounts-twitter-callback')
    )
    try:
        authorization_url = auth.get_authorization_url(signin_with_twitter=True)
    except tweepy.TweepError, e:
        return render_to_response(
            'accounts/twitter_error.html',
            dict(twitter_error_message=unicode(e)),
            context_instance=RequestContext(request)
        )
    else:
        request.session['TWITTER_REQUEST_TOKEN'] = dict(key=auth.request_token.key, secret=auth.request_token.secret)

    return HttpResponseRedirect(authorization_url)

@transaction.commit_on_success
def process_callback(request):
    '''
    Handles callback redirect from Twitter during OAuth post-authentication step.

    * URL Name

      ``accounts-twitter-callback``

    * Available Context

      ``twitter_error_message`` - Set only when Twitter authentication results in an exception.

    * Template

      'accounts/twitter_error.html' - Used only when Twitter authentication results in an exception. Otherwise none.

    '''
    if request.GET.get('denied'):
        return render_to_response(
            'accounts/twitter_error.html',
            dict(twitter_error_message=u'Application access to your Twitter account was denied.'),
            context_instance=RequestContext(request)
        )

    oauth_token = request.GET.get('oauth_token', None)
    oauth_verifier = request.GET.get('oauth_verifier', None)

    if oauth_token is None:
        raise Http404

    request_token = request.session.get('TWITTER_REQUEST_TOKEN')
    if request_token is None:
        raise Http404

    auth = tweepy.OAuthHandler(
        settings.TWITTER_CONSUMER_KEY,
        settings.TWITTER_CONSUMER_SECRET
    )
    try:
        auth.set_request_token(request_token['key'], request_token['secret'])
        auth.get_access_token(oauth_verifier)
        api = tweepy.API(auth)
        credentials = api.me()
    except tweepy.TweepError, e:
        return render_to_response(
            'accounts/twitter_error.html',
            dict(twitter_error_message=unicode(e)),
            context_instance=RequestContext(request)
        )

    if request.user.is_authenticated():
        profile = request.user.get_profile()
        profile.twitter_id = credentials.screen_name
        profile.twitter_access_token = auth.access_token
        profile.save()
    else:
        from django.contrib.auth import authenticate as django_authenticate, login as django_login

        try:
            user = django_authenticate(token=auth.access_token, request=request)
        except tweepy.TweepError, e:
            return render_to_response(
                'accounts/twitter_error.html',
                dict(twitter_error_message=unicode(e)),
                context_instance=RequestContext(request)
            )

        if user is not None:
            django_login(request, user)
        else:
            return HttpResponseRedirect(url_for_view('accounts-postauthcmd'))

    request.session['authentication'] = dict(
        method='twitter',
        name=u'@%s' % credentials.screen_name,
    )
    return accounts.post_auth_redirect(request)

def get_twitter_client():
    if hasattr(_thread_locals, 'twitter'):
        return _thread_locals.twitter
    else:
        return None

class TwitterClientMiddleware(object):
    def process_request(self, request):
        if request.session.get('authentication') and 'twitter' == request.session['authentication']['method']:
            import cgi

            access_token = cgi.parse_qs(request.user.get_profile().twitter_access_token)
            auth = tweepy.OAuthHandler(
                settings.TWITTER_CONSUMER_KEY,
                settings.TWITTER_CONSUMER_SECRET
            )
            auth.set_access_token(access_token['oauth_token'][0], access_token['oauth_token_secret'][0])
            api = tweepy.API(auth)
            if api.verify_credentials():
                _thread_locals.twitter = request.twitter = api

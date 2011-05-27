from django.conf import settings
from django.core.urlresolvers import reverse as url_for_view
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.core.files import File
from models import UserProfile

import accounts, utils
import fb_utils

xd_receiver_htm = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"> <html xmlns="http://www.w3.org/1999/xhtml" > <body> <script src="http://static.ak.connect.facebook.com/js/api_lib/v0.4/XdCommReceiver.js" type="text/javascript"></script> </body></html> 
'''

class FacebookAuthenticationBackend(object):
    def authenticate(self, **credentials):
        fb = credentials.get('fb')
        request = credentials.get('request')
        if fb is None:
            return None
        
        username = 'fb_%s' % (str(fb.uid))
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Check to see if we already have a UserProfile with the fb.uid in
            # store. This is so that we can allow users to change their default
            # Django auth usernames.
            try:
                profile = UserProfile.objects.get(facebook_id=fb.uid)
                user = profile.user
            except UserProfile.DoesNotExist:
                user = User(username=username)
                user.set_password(utils.get_random_password())
                user.save()
                profile = user.get_profile()
                profile.facebook_id = fb.uid
                try:
                    user_info = fb.users.getInfo(fb.uid, fields=['first_name'])[0]
                    profile.facebook_name = user_info['first_name']
                except:
                    pass
                profile.save()
                request.session['is_new_user_account'] = True

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

def xd_receiver(request):
    '''
    Returns the xd_receiver.htm file required by Facebook Connect.

    * URL Name

      ``accounts-fbconnect-xd_receiver``

    * Available Context

      None.

    * Template

      None.

    '''
    return HttpResponse(xd_receiver_htm)

@transaction.commit_on_success
def authenticate(request):
    '''
    Performs Facebook Connect authentication.

    * URL Name

      ``accounts-fbconnect-authenticate``

    * Available Context

      None.

    * Template

      None.

    '''
    #import ipdb
    #ipdb.set_trace()
    fb = request.facebook
    user = None
    if fb.check_session(request):
        if request.user.is_authenticated():
            profile = request.user.get_profile()
            profile.facebook_id = fb.uid
            profile.save()
            user = request.user
        else:
            from django.contrib.auth import authenticate, login

            user = authenticate(fb=fb, request=request)

            if user is not None:
                login(request, user)
            else:
                return HttpResponseRedirect(url_for_view('accounts-postauthcmd'))
        
        user_info = fb.users.getInfo(fb.uid, fields=['first_name','pic'])[0]
        file_url = fb_utils.get_image_fb(user_info['pic'])
        profile_extension = user.profile_extensions.get()
        pic_name = file_url.split('/')[-1]
        profile_extension.picture.save(pic_name,File(open(file_url)))

        request.session['authentication'] = dict(
            method='facebook',
            name=user_info['first_name'],
        )
        return accounts.post_auth_redirect(request)
    else:
        return HttpResponseRedirect(url_for_view('accounts-postauthcmd'))

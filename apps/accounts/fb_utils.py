import os,urllib
import Image
from django.db import connection
from django.conf import settings


def get_image_fb(url):
    """
    get the image from fb (the regular one)
    and then save it to our folder, and set the profile pic with 
    that pic.
    """
    file_name = url.split('/')[-1]
    location = os.path.join(settings.PROJECT_ROOT, 'uploads/fb_profile')
    if not os.path.exists(location):
        os.makedirs(location)
    file_name_url = os.path.join(location,file_name)
    urllib.urlretrieve (url, file_name_url)
    try:
        im = Image.open(file_name_url)
    except Exception,e:
        return None

    return file_name_url


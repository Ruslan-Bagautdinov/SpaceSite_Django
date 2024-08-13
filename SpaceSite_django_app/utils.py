# myapp/utils.py
import os
import random

import requests
from django.conf import settings
from django.shortcuts import redirect
from rest_framework import status


def set_top_message(request,
                    message_class,
                    message_icon,
                    message_text):
    request.session.pop('top_message', None)
    top_message = {
        "class": message_class,
        "icon": message_icon,
        "text": message_text
    }
    request.session['top_message'] = top_message


def redirect_with_message(request,
                          message_class,
                          message_icon,
                          message_text,
                          status=status.HTTP_302_FOUND,
                          endpoint=None, logout=False):
    top_message = {
        "class": message_class,
        "icon": message_icon,
        "text": message_text
    }
    request.session['top_message'] = top_message
    if logout:
        endpoint = "/logout/?login=True"
    return redirect(endpoint, status=status)


def load_unsplash_photo(query: str = "cosmos") -> str | None:
    url = "https://api.unsplash.com/search/photos"
    headers = {
        "Accept-Version": "v1",
        "Authorization": f"Client-ID {settings.UNSPLASH_ACCESS_KEY}"
    }
    params = {
        "query": query,
        "orientation": "landscape",
        "per_page": 50
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get('results'):
            random_index = random.randint(0, len(data['results']) - 1)
            image_url = data['results'][random_index]['urls']['regular']
        else:
            image_url = None
    except requests.HTTPError as errh:
        print("HTTP error occurred:", errh)
        image_url = None
    except requests.RequestException as err:
        print("An error occurred:", err)
        image_url = None

    return image_url


def get_user_photo_url(profile):
    user_photo_path = profile.user_photo
    if user_photo_path:
        user_photo_full_path = os.path.join(settings.BASE_DIR, 'static', 'img', user_photo_path)
        if os.path.exists(user_photo_full_path):
            user_photo_url = os.path.join(settings.STATIC_URL, 'img', user_photo_path)
        else:
            user_photo_url = os.path.join(settings.STATIC_URL, 'img', 'default_avatar.jpg')
    else:
        user_photo_url = os.path.join(settings.STATIC_URL, 'img', 'default_avatar.jpg')
    return user_photo_url

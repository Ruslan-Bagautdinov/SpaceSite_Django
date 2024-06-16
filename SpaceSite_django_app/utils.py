# myapp/utils.py
import requests
import random
from django.conf import settings
from django.shortcuts import redirect


def redirect_with_message(request, message_class, message_icon, message_text, endpoint=None, logout=False):
    top_message = {
        "class": message_class,
        "icon": message_icon,
        "text": message_text
    }
    request.session['top_message'] = top_message
    if logout:
        endpoint = "/logout/?login=True"
    return redirect(endpoint)


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


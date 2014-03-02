import urllib
import urllib2
import json
import webbrowser
import hashlib

API_BASE_URL = "http://ws.audioscrobbler.com/2.0/"
API_KEY = "015c5b2bc2f58dbc242e1819489b5368"
SECRET = "6233244f27aee20b96c5cbeae2b94127"


def get_user_auth_url(token):
    params = {
        'api_key': API_KEY,
        'token': token
    }
    return build_url('http://www.last.fm/api/auth/', params)


def get_session(token):
    params = {
        'method': 'auth.getSession',
        'token': token,
        'api_key': API_KEY
    }
    data = get_json_response(params)
    return data['session']['key']


def get_auth_token():
    params = {
        'method': 'auth.getToken',
        'api_key': API_KEY
    }
    data = get_json_response(params)
    return data['token']


def get_json_response(params):
    params['format'] = 'json'
    res = get_response(params)
    return json.loads(res)


def get_response(params):
    params['api_sig'] = get_api_sig(params)
    url = build_url(API_BASE_URL, params)
    return urllib2.urlopen(url).read()


def get_api_sig(params):
    str = ''
    # Concatenate key-value pairs from the query string, sorted alphabetically by key
    for item in sorted(params.items()):
        if item[0] != 'format':  # API bug: Request fails if format parameter is included in the digest
            str += item[0]
            str += item[1]
    str += SECRET
    str = str.encode('UTF-8')  # Force UTF-8 encoding (probably started as Unicode)
    str = hashlib.md5(str).hexdigest()
    return str


def build_url(url, params):
    q_string = urllib.urlencode(params)
    return url + '?' + q_string


class Session:

    def __init__(self):
        self._token = None
        self.session_key = None

    def is_active(self):
        return self._token is None

    def get_token(self):
        if not self._token:
            self._token = get_auth_token()
        return self._token

    def reset_token(self):
        self._token = None

    def authenticate_user(self):
        url = get_user_auth_url(self.get_token())
        webbrowser.open_new_tab(url)
        self.session_key = get_session(self.get_token())
        self.reset_token()  # Tokens may only be used once

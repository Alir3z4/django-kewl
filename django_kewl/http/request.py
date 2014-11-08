import os
from django.conf import settings


def build_absolute_url(path):
    """
    To build absolute URL with this helper, you need to define site
    domain in ``settings``.

    >>> SITE = {
    >>>     'name': 'Awesome Site',
    >>>     'domain': 'awesome.<3',
    >>>}

    >>> from django_kewl.http.request import build_absolute_url
    >>>
    >>>
    >>> path = '/users/register'
    >>> absolute_path = build_absolute_url(path)
    >>> assert path != absolute_path
    >>> assert absolute_path.endswith('/')
    >>> assert absolute_path.startswith('http://')
    >>> # Let's say we're having fun with SSL
    >>> os.environ.setdefault('wsgi.url_scheme', 'https')
    >>> absolute_path = build_absolute_url(path)
    >>> assert absolute_path.startswith('https://')


    :param path: path to build the absolute URL for.
    :type path: str

    :rtype: str
    """
    url_scheme = os.environ.get('wsgi.url_scheme', 'https')

    if not path.endswith('/'):
        path = '{0}/'.format(path)

    return '{0}://{1}{2}'.format(url_scheme, settings.SITE['domain'], path)

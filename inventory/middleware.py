from django.conf import settings


def _is_cloud_tunnel(request):
    host = request.get_host().split(':')[0]
    origin = request.META.get('HTTP_ORIGIN', '')
    forwarded_host = request.META.get('HTTP_X_FORWARDED_HOST', '')
    return (
        host.endswith('.cvm.dev')
        or host.endswith('.agent.cvm.dev')
        or '.agent.cvm.dev' in origin
        or '.cvm.dev' in forwarded_host
    )


class CloudDevMiddleware:
    """
    يضبط HTTPS/CSRF تلقائياً عند الوصول عبر Cursor Cloud Agent أو أنفاق مشابهة.
    يحل: Origin checking failed / CSRF cookie not set
    """

    _SETTING_KEYS = (
        'SECURE_PROXY_SSL_HEADER',
        'USE_X_FORWARDED_HOST',
        'CSRF_COOKIE_SECURE',
        'SESSION_COOKIE_SECURE',
        'CSRF_COOKIE_SAMESITE',
        'SESSION_COOKIE_SAMESITE',
        'CSRF_USE_SESSIONS',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not _is_cloud_tunnel(request):
            return self.get_response(request)

        saved = {key: getattr(settings, key, None) for key in self._SETTING_KEYS}
        added_origin = None

        settings.SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
        settings.USE_X_FORWARDED_HOST = True
        settings.CSRF_COOKIE_SECURE = True
        settings.SESSION_COOKIE_SECURE = True
        settings.CSRF_COOKIE_SAMESITE = 'Lax'
        settings.SESSION_COOKIE_SAMESITE = 'Lax'
        settings.CSRF_USE_SESSIONS = True

        origin = request.META.get('HTTP_ORIGIN', '')
        if origin and origin not in settings.CSRF_TRUSTED_ORIGINS:
            settings.CSRF_TRUSTED_ORIGINS.append(origin)
            added_origin = origin

        if not request.META.get('HTTP_X_FORWARDED_PROTO'):
            request.META['HTTP_X_FORWARDED_PROTO'] = 'https'

        try:
            return self.get_response(request)
        finally:
            for key, value in saved.items():
                setattr(settings, key, value)
            if added_origin and added_origin in settings.CSRF_TRUSTED_ORIGINS:
                settings.CSRF_TRUSTED_ORIGINS.remove(added_origin)

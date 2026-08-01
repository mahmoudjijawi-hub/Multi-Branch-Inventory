from django.conf import settings


class DevTrustedOriginMiddleware:
    """
    في وضع التطوير: يثق تلقائياً بـ Origin للطلب الحالي.
    يحل مشكلة CSRF عند الوصول عبر أنفاق التطوير (Cursor Cloud, ngrok, ...).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        origin = request.META.get('HTTP_ORIGIN', '')
        if not origin:
            return self.get_response(request)

        host = request.get_host().split(':')[0]
        is_dev_tunnel = (
            settings.DEBUG
            or host.endswith('.cvm.dev')
            or '.agent.cvm.dev' in origin
        )
        if is_dev_tunnel and origin not in settings.CSRF_TRUSTED_ORIGINS:
            settings.CSRF_TRUSTED_ORIGINS.append(origin)

        return self.get_response(request)

"""تضمين ملفات CSS/JS مباشرة في HTML — يضمن ظهور التصميم حتى لو فشل WhiteNoise."""
from pathlib import Path

from django import template
from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.utils.safestring import mark_safe

register = template.Library()

_cache = {}


def _read_static(path: str) -> str:
    if path in _cache:
        return _cache[path]

    content = ''
    found = find(path)
    if found:
        content = Path(found).read_text(encoding='utf-8')
    else:
        # احتياطي: اقرأ من STATIC_ROOT بعد collectstatic
        root_file = Path(settings.STATIC_ROOT) / path
        if root_file.exists():
            content = root_file.read_text(encoding='utf-8')
        else:
            # احتياطي أخير: المجلد المصدر
            src = Path(settings.BASE_DIR) / 'static' / path
            if src.exists():
                content = src.read_text(encoding='utf-8')

    if not settings.DEBUG:
        _cache[path] = content
    return content


@register.simple_tag
def inline_css(path):
    return mark_safe(f'<style>\n{_read_static(path)}\n</style>')


@register.simple_tag
def inline_js(path):
    return mark_safe(f'<script>\n{_read_static(path)}\n</script>')

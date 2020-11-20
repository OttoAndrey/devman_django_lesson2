from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from banners.models import Banner


def banner_detail_view(request, slug):
    banner = get_object_or_404(Banner, slug=slug)

    data = {
            'title': banner.title,
            'src': banner.image.url,
            'text': banner.text,
            'active': banner.active,
            'slug': banner.slug
        }

    return JsonResponse(data, json_dumps_params={'ensure_ascii': False, 'indent': 4})

from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from banners.models import Banner
from banners.serializers import BannerSerializer


@api_view(['GET'])
def banner_detail_view(request, slug):
    banner = get_object_or_404(Banner, slug=slug)
    serializer = BannerSerializer(banner)

    return Response(serializer.data)

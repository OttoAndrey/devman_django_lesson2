from rest_framework import serializers

from banners.models import Banner


class BannerSerializer(serializers.ModelSerializer):
    """Serializer for Banner model."""

    class Meta:
        model = Banner
        fields = [
            "title",
            "text",
            "active",
            "slug",
            "image",
        ]

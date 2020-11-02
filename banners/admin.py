from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django.utils.html import format_html

from .models import Banner


@admin.register(Banner)
class BannerAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = [
        'title',
        'text',
        'active',
        'get_image_preview',
    ]
    list_editable = ['active']
    readonly_fields = ['get_image_preview']
    prepopulated_fields = {'slug': ['title']}

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{src}" height="100" width="200"/>', src=obj.image.url)
    get_image_preview.short_description = 'превью'

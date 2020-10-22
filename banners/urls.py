from django.urls import path

from banners.views import banner_detail_view

app_name = "banners"


urlpatterns = [
    path('<slug:slug>/', banner_detail_view, name='banner_detail')
]

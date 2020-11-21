from django.urls import path

from .views import UsersViewSet

app_name = "users"

urlpatterns = [
    path(f'{app_name}/reg/', UsersViewSet),
    path(f'{app_name}/auth/', UsersViewSet),
]

from rest_framework import routers

from users.views import UsersViewSet, CustomAuthToken

router = routers.DefaultRouter()
router.register('reg', UsersViewSet, basename='reg')

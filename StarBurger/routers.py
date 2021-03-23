from rest_framework import routers

from users.views import CreateUserViewSet

router = routers.DefaultRouter()
router.register('reg', CreateUserViewSet, basename='reg')

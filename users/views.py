from django.contrib.auth.models import User
from rest_framework import mixins, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from users.serializers import UsersSerializer


class CreateUserViewSet(
        mixins.CreateModelMixin,
        GenericViewSet,
):
    serializer_class = UsersSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.create(**serializer.data)
        user.set_password(serializer.data['password'])
        user.save()

        headers = self.get_success_headers(serializer.data)
        token = Token.objects.create(user=user)

        return Response(
            {'username': serializer.data['username'], 'token': token.key},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class CustomAuthToken(ObtainAuthToken):
    """Custom class which expects username and password and returns token.

    Used custom class instead `obtain_auth_token` just for practice.
    """
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'username': user.username,
            'token': token.key,
        })

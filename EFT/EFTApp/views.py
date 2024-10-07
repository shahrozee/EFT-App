import io
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.db import connections, transaction
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login
from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Count
from rest_framework.exceptions import ValidationError
from rest_framework import status, filters, viewsets
from django.http import JsonResponse
import requests
from rest_framework.decorators import action
from rest_framework.response import Response
import os
from .serializers import *


class LoginViewSet(viewsets.ViewSet):
    def create(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email:
            return Response(
                {"message": "Kindly fill email's field", "data": {}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not password:
            return Response(
                {"message": "Kindly fill password's field", "data": {}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = CustomUser.objects.filter(email=email).first()
        if user and user.check_password(password):
            user = authenticate(request, username=user.username, password=password)
            login(request, user)
            expiration_time = datetime.now() + timedelta(days=1)
            refresh_expiration_time = datetime.now() + timedelta(days=6)
            token = RefreshToken.for_user(user)
            data = {
                "refresh_token": str(token),
                "access_token": str(token.access_token),
                "refresh_token_expiry": refresh_expiration_time,
                "access_token_expiry": expiration_time,
                "id": user.id,
                "username": user.username,
                "user_email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name
            }
            return Response(
                {"message": "Logged in successfully", "data": data},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": "Invalid username or password.", "data": {}},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserSignupViewSet(viewsets.ModelViewSet):
    serializer_class = UserSignupSerializer
    http_method_names = ["post", "put", "patch", "delete"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": "User created successfully.", "data": serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def perform_create(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        user = self.get_object()  # Get the user instance
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            {"message": "User updated successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)  # Same as update for this case

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()  # Get the user instance
        user.delete()
        return Response(
            {"message": "User deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )

    def get_object(self):
        user_id = self.kwargs.get('pk')
        return get_object_or_404(CustomUser, id=user_id)

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class CustomUserManger(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        # 슈퍼유저의 경우 is_superuser와 is_staff를 True로 설정합니다.
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        # is_superuser와 is_staff가 True로 설정되었는지 확인합니다.
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        # 나머지는 일반 유저 생성과 동일합니다.
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    profile_image = models.ImageField("프로필 이미지", upload_to="users/profile", blank=True)
    short_description = models.TextField("소개글", blank=True)
    objects = CustomUserManger()

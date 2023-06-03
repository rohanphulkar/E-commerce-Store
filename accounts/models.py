from django.db import models
from .manager import UserManager
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
import uuid
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

class User(AbstractBaseUser,PermissionsMixin):
    id  = models.UUIDField(default=uuid.uuid4,editable=False,primary_key=True)
    name = models.CharField(max_length=255,blank=True,null=True)
    email = models.EmailField(unique=True,verbose_name="email",max_length=60)
    username = models.CharField(max_length=255,blank=True,null=True)
    phone = models.CharField(max_length=15,blank=True,null=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=255, blank=True, null=True)
    pwd_reset_token = models.CharField(max_length=255, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
    

    # For checking permissions. to keep it simple all admin have ALL permissons
    def has_perm(self, perm, obj=None):
            return self.is_admin

    def has_module_perms(self, app_label):
            return self.is_admin
          
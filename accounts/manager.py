from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self,email,password=None):
        if not email:
            raise ValueError("Email address is required")
        if not password:
            raise ValueError("Password is required")
        
        user = self.model(
            email = self.normalize_email(email),
        )

        user.set_password(password)

        user.save()
        return user
    
    def create_superuser(self,email,password=None):
        if password is None:
            raise ValueError("Password is required")
        
        user = self.create_user(
            email = email,
            password = password
        )

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_verified = True
        user.save()
        return user
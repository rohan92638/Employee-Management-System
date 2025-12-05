from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, full_name, mobile, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        email= self.normalize_email(email)
        user= self.model(email= email, full_name= full_name, mobile= mobile)
        user.set_password(password)
        user.save(using= self._db)
        return user
    
    def create_superuser(self, email, full_name, mobile, password):
        user= self.create_user(email, full_name, mobile, password)
        user.is_staff= True     # Admin panel access
        user.is_superuser= True     # Sab permissions
        user.save(using= self._db)
        return user
    
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=50)
    mobile = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
     # IMPORTANT: Add related_name to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',  # <- change here
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set_permissions',  # <- change here
        blank=True
    )

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'mobile']

    def __str__(self):
        return self.email
    
    
    
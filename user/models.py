from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


from django.db import models

from user.managers import CustomUserManager

# class User(AbstractUser):
#     USER_CHOICES = (
#         ('candidate', 'candidate'),
#         ('recruiter', 'recruiter'),
#     )
#     USERNAME_FIELD = 'username'
#     user_role = models.CharField(max_length=10, choices=USER_CHOICES)
#     otp = models.CharField(max_length=6, blank=True, null=True)
#     otp_created_at = models.DateTimeField(auto_now_add=True)
#     email_verification = models.BooleanField(default=False)
            
#     first_name = None
#     last_name = None
    

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"), unique=True)  
    user_role = models.CharField(max_length=10)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    


class CompanyProfile(models.Model):
    COMPANY_CATEGORY_CHOICES = (
        ('IT','IT'),
        ('BANKING', 'BANKING'),
    )

    COMPANY_TYPE_CHOICES = (
        ('HYBRID', 'HYBRID'),
        ('REMOTE', 'REMOTE'),
    )

    COMPANY_SIZE_CHOICES = (
        ('1-50', '1-50'),
        ('50-100', '50-100'),
        ('100-150', '100-150'),
        ('150-200', '150-200')
    )
    name = models.CharField(max_length=150)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=150, unique=True)
    company_mail = models.EmailField()
    contact_no_regex = RegexValidator(regex=r'^\d{10}$')
    contact_number = models.CharField(validators=[contact_no_regex], max_length=10)
    company_website = models.URLField(max_length=200, blank=True, null=True)
    company_logo = models.ImageField(upload_to='logo/', blank=True, null=True)
    company_category = models.CharField(max_length=100,choices=COMPANY_CATEGORY_CHOICES)
    company_type = models.CharField(max_length=100,choices=COMPANY_TYPE_CHOICES)
    company_size = models.CharField(max_length=100,choices=COMPANY_SIZE_CHOICES)
    min_payroll = models.DecimalField(max_digits=10, decimal_places=2)
    company_headquarter = models.CharField(max_length=100)
    company_headquarter_country = models.CharField(max_length=50)
    company_branches = models.JSONField(null=True, blank=True)

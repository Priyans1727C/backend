# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# ------------------------------
# Custom User Model
# ------------------------------

class User(AbstractUser):
    """
    Custom user model that extends the built-in AbstractUser.
    Additional fields include role and status.
    """
    class Role(models.TextChoices):
        CUSTOMER = 'customer', 'Customer'
        SHOP_OWNER = 'shop_owner', 'Shop Owner'
        ADMIN = 'admin', 'Admin'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
        help_text=_("Designates the role of the user."),
    )
    status = models.CharField(
        max_length=20,
        default='active',
        help_text=_("Account status, e.g. active, inactive, or suspended."),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',  # Avoids name clash
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',  # Avoids name clash
        blank=True
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


# ------------------------------
# UserProfile Model
# ------------------------------

class UserProfile(models.Model):
    """
    Stores additional personal details for a user.
    Has a one-to-one relationship with the User model.
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile'
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=20, blank=True, null=True)
    profile_pic = models.ImageField(
        upload_to='profile_pics/', blank=True, null=True,
        help_text=_("Upload a profile picture.")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


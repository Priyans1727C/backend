from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, UserProfile

class CustomUserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ['id','username', 'email', 'role', 'status', 'is_active']

admin.site.register(User, CustomUserAdmin)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'phone')
    search_fields = ('user__username', 'first_name', 'last_name')
    list_filter = ('user__is_staff',)
    ordering = ('user__date_joined',)
    list_per_page = 20
    
admin.site.register(UserProfile, UserProfileAdmin)


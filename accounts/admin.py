from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

# Register your models here.
class UserModelAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'name', 'city', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    fieldsets = [
        ("User Credential", {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'city')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    ]
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'city', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

admin.site.register(User, UserModelAdmin)
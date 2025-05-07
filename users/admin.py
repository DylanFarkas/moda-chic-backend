from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Wishlist, Cart

# Register your models here.
admin.site.register(Wishlist)
admin.site.register(Cart)

class CustomUserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'username', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_customer')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_admin', 'is_customer', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'username')
    ordering = ('email',)
    
admin.site.register(User, CustomUserAdmin)

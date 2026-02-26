from django.contrib import admin
from .models import CustomUser, Role

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'display_roles', 'organization', 'is_staff', 'is_active', 'approval_status')
    list_filter = ('is_staff', 'is_active', 'approval_status', 'organization')
    search_fields = ('email',)
    ordering = ('email',)

    def display_roles(self, obj):
        return ", ".join([role.name for role in obj.roles.all()])
    display_roles.short_description = 'Roles'

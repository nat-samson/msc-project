from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    """ Add user management tools to the Django Admin site """
    model = User
    list_display = ('last_name', 'first_name', 'is_teacher', 'is_superuser', 'is_active',)
    list_filter = ('is_teacher', 'is_superuser', 'is_active')
    ordering = ('last_name',)
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_teacher',)}),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set()

        # prevent non-admin staff members from escalating their own privileges
        if (
                not is_superuser
                and obj is not None
                and obj == request.user
        ):
            disabled_fields |= {
                'is_teacher',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            }

        for field in disabled_fields:
            if field in form.base_fields:
                form.base_fields[field].disabled = True

        return form

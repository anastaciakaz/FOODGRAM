from django.contrib import admin

from users.models import Follow, User


class UserAdmin(admin.ModelAdmin):
    """Админ панель для модели User."""
    list_filter = ('username', 'email')


admin.site.register(User, UserAdmin)
admin.site.register(Follow)

from django.contrib import admin
from django.contrib.admin import ModelAdmin
from user.models import Transaction, CustomUser, Inn
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    ordering = ('id',)
    list_display = ('id', 'username', 'balance', 'inn')
    list_filter = ('inn',)
    fieldsets = (
        (None, {
            'fields': ('username', 'balance', 'inn')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
        ('Important date', {
            'fields': ('last_login',)
        })
    )


class TransactionAdmin(ModelAdmin):
    model = Transaction
    list_display = ('pk', 'out_user', 'amount', 'created_at', 'users')

    def users(self, obj):
        return obj.in_users.count()


class InnAdmin(ModelAdmin):
    model = Inn
    ordering = ('-pk',)
    list_display = ('pk', 'number', 'users')

    def users(self, obj):
        return obj.users.count()


admin.site.register(Transaction, TransactionAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Inn, InnAdmin)

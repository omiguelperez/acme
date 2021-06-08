from django.contrib import admin

from src.workflow.models import Account, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = ('id', 'user_id',)
    readonly_fields = ('id',)
    search_fields = ('user_id',)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):

    list_display = ('id', 'user', 'balance',)
    readonly_fields = ('id',)
    autocomplete_fields = ('user',)
    search_fields = ('user__user_id',)

from django.db import models

from django.contrib import admin
from prettyjson import PrettyJSONWidget

from src.workflow.models import Account, User, Upload


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


@admin.register(Upload)
class UploadAdmin(admin.ModelAdmin):

    formfield_overrides = {
        models.JSONField: {'widget': PrettyJSONWidget}
    }
    readonly_fields = ('id', 'file', 'success',)
    list_display = ('id', 'file',)

from django.contrib import admin

from zs.apps.core.models import AppSetting

@admin.register(AppSetting)
class AppSettingAdmin(admin.ModelAdmin):
    list_display = ["key", "value"]

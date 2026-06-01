from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "created_at", "status")
    list_filter = ("status", "created_at")
    search_fields = ("name", "owner__email", "owner__name", "owner__surname")
    raw_id_fields = ("owner", "participants")

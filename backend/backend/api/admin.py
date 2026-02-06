from django.contrib import admin
from .models import PDF, Roadmap, InterviewQuestion


# ---------- PDF ADMIN ----------
@admin.register(PDF)
class PDFAdmin(admin.ModelAdmin):
    list_display = ("title", "is_approved", "created_at")
    list_filter = ("is_approved", "created_at")
    search_fields = ("title",)
    actions = ["approve_selected", "unapprove_selected"]

    def approve_selected(self, request, queryset):
        queryset.update(is_approved=True)
    approve_selected.short_description = "Approve selected PDFs"

    def unapprove_selected(self, request, queryset):
        queryset.update(is_approved=False)
    unapprove_selected.short_description = "Unapprove selected PDFs"


# ---------- ROADMAP ADMIN ----------
@admin.register(Roadmap)
class RoadmapAdmin(admin.ModelAdmin):
    list_display = ("title", "is_approved", "created_at")
    list_filter = ("is_approved", "created_at")
    search_fields = ("title",)
    actions = ["approve_selected", "unapprove_selected"]

    def approve_selected(self, request, queryset):
        queryset.update(is_approved=True)
    approve_selected.short_description = "Approve selected Roadmaps"

    def unapprove_selected(self, request, queryset):
        queryset.update(is_approved=False)
    unapprove_selected.short_description = "Unapprove selected Roadmaps"


# ---------- INTERVIEW QUESTION ADMIN ----------
@admin.register(InterviewQuestion)
class InterviewQuestionAdmin(admin.ModelAdmin):
    list_display = ("company", "role", "is_approved", "created_at")
    list_filter = ("is_approved", "created_at")
    search_fields = ("company", "role")
    actions = ["approve_selected", "unapprove_selected"]

    def approve_selected(self, request, queryset):
        queryset.update(is_approved=True)
    approve_selected.short_description = "Approve selected Interview PDFs"

    def unapprove_selected(self, request, queryset):
        queryset.update(is_approved=False)
    unapprove_selected.short_description = "Unapprove selected Interview PDFs"

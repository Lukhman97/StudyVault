from django.urls import path
from .views import *


urlpatterns = [

    path("signup/", signup),
    path("login/", login),

    path("pdfs/", pdfs),
    path("roadmaps/", roadmaps),
    path("interviews/",interview_questions),

    # ✅ download counters
    path("pdfs/<int:pk>/download/", pdf_download),
    path("roadmaps/<int:pk>/download/", roadmap_download),
    path("interviews/<int:pk>/download/", interview_download),

    # view counters

    path("pdfs/<int:pk>/view/", increment_pdf_view),
    path("roadmaps/<int:pk>/view/", increment_roadmap_view),
    path("interviews/<int:pk>/view/", increment_interview_view),

    # admin
    path("admin/pdfs/",admin_pdfs),
path("admin/pdfs/<int:pk>/approve/",approve_pdf),

path("admin/roadmaps/",admin_roadmaps),
path("admin/roadmaps/<int:pk>/approve/",approve_roadmap),

path("admin/interviews/",admin_interviews),
path("admin/interviews/<int:pk>/approve/",approve_interview),

path("admin/pdfs/<int:pk>/reject/", reject_pdf),
path("admin/roadmaps/<int:pk>/reject/", reject_roadmap),
path("admin/interviews/<int:pk>/reject/", reject_interview),


]
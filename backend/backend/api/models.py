from django.db import models


class PDF(models.Model):
    title = models.CharField(max_length=200)
    file_url = models.URLField()
    image_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    # admin approval
    is_approved = models.BooleanField(default=False)

    # download count
    download_count = models.PositiveIntegerField(default=0)

    # views count
    view_count = models.PositiveIntegerField(default=0)  


    def __str__(self):
        return self.title


class Roadmap(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    # admin approval
    is_approved = models.BooleanField(default=False)

    # download count
    download_count = models.PositiveIntegerField(default=0)

    # views count
    view_count = models.PositiveIntegerField(default=0)   # 👁️ NEW


    def __str__(self):
        return self.title


class InterviewQuestion(models.Model):
    company = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    pdf_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    # admin approval
    is_approved = models.BooleanField(default=False)

    # download count
    download_count = models.PositiveIntegerField(default=0)

    # view count
    view_count = models.PositiveIntegerField(default=0) 


    def __str__(self):
        return f"{self.company} - {self.role}"

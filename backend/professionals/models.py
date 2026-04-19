from django.db import models


class Professional(models.Model):
    class Source(models.TextChoices):
        DIRECT = 'direct', 'Direct'
        PARTNER = 'partner', 'Partner'
        INTERNAL = 'internal', 'Internal'

    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    job_title = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=32, unique=True, null=True, blank=True)
    source = models.CharField(max_length=16, choices=Source.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', 'id']

    def __str__(self):
        return self.full_name

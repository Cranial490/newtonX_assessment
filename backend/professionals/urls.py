from django.urls import path

from professionals.views import (
    ProfessionalBulkView,
    ProfessionalCsvUploadView,
    ProfessionalView,
)


app_name = 'professionals'

urlpatterns = [
    path('', ProfessionalView.as_view(), name='professional-list'),
    path('bulk/', ProfessionalBulkView.as_view(), name='professional-bulk'),
    path('upload/csv/', ProfessionalCsvUploadView.as_view(), name='professional-upload-csv'),
]

from django.urls import path

from professionals.views import (
    ProfessionalBulkView,
    ProfessionalCsvUploadView,
    ProfessionalStatsView,
    ProfessionalView,
)


app_name = 'professionals'

urlpatterns = [
    path('stats/', ProfessionalStatsView.as_view(), name='professional-stats'),
    path('', ProfessionalView.as_view(), name='professional-list'),
    path('bulk/', ProfessionalBulkView.as_view(), name='professional-bulk'),
    path('upload/csv/', ProfessionalCsvUploadView.as_view(), name='professional-upload-csv'),
]

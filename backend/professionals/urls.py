from django.urls import path

from professionals.views import ProfessionalBulkView, ProfessionalView


app_name = 'professionals'

urlpatterns = [
    path('', ProfessionalView.as_view(), name='professional-list'),
    path('bulk/', ProfessionalBulkView.as_view(), name='professional-bulk'),
]

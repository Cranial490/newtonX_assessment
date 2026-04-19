from django.urls import path

from professionals.views import ProfessionalView


app_name = 'professionals'

urlpatterns = [
    path('', ProfessionalView.as_view(), name='professional-create'),
]

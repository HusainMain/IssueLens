
from django.urls import path
from django.urls import path
from .views import (
    api_status,
    repository_details,
    repository_issues,
    search_github_issues,
)

urlpatterns = [
    path('status/', api_status, name='api_status'),
    path('repository/', repository_details, name='repository_details'),
    path('repository/issues/', repository_issues, name='repository_issues'),
    path('search/', search_github_issues, name='search_github_issues'),
]

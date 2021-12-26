from django.urls import path
from .views import VisitedLinks, VisitedDomains


urlpatterns = [
    path('visited_links/', VisitedLinks.as_view(), name='visited_links'),
    path('visited_domains/', VisitedDomains.as_view(), name='visited_links'),
]

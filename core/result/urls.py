# urls.py
from django.urls import path
from .views import (
    ResultListView,
    ResultCreateView,
    ResultUpdateView,
    ResultDeleteView,
)

urlpatterns = [
    path("", ResultListView.as_view(), name="result-list"),
    path("create/", ResultCreateView.as_view(), name="result-create"),
    path("<int:pk>/update/", ResultUpdateView.as_view(), name="result-update"),
    path("<int:pk>/delete/", ResultDeleteView.as_view(), name="result-delete"),
]

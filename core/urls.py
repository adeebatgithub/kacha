from django.urls import path, include

from .views import DashboardView, ScoreBoardView, ScoreboardSSEView

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('', ScoreBoardView.as_view(), name='scoreboard'),
    path('scoreboard/stream/', ScoreboardSSEView.as_view(), name='scoreboard_stream'),

    path('events/', include("core.event.urls")),
    path('team/', include("core.team.urls")),
    path('result/', include("core.result.urls")),
]
import json
import time

from django.core.cache import cache
from django.db.models import Q, Count
from django.http import StreamingHttpResponse
from django.views import View
from django.views.generic import TemplateView

from .models import Team, Event


class DashboardView(TemplateView):
    template_name = 'dashboard.html'


class ScoreBoardView(TemplateView):
    template_name = "scoreboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Initial data for page load, then WebSocket takes over
        context.update({"teams": self.get_ranked_teams(), "recent_event": self.get_recent_results()})
        return context

    def get_recent_results(self):
        events = (Event.objects.annotate(
            podium_count=Count("results", filter=Q(results__position__in=[1, 2, 3]), distinct=True)).filter(
            podium_count=3).order_by("-id")[:5].prefetch_related("results"))
        return events

    def get_ranked_teams(self):
        teams = Team.objects.all()
        teams_with_points = []
        for team in teams:
            teams_with_points.append({'id': team.id, 'name': team.name, 'points': team.points})
        teams_with_points.sort(key=lambda x: x['points'], reverse=True)
        return teams_with_points


# Updated SSE view with signal support
class ScoreboardSSEView(View):
    def get(self, request):
        def event_stream():
            last_state = None
            while True:
                # Check if update is needed
                needs_update = cache.get('scoreboard_needs_update', False)

                if needs_update or last_state is None:
                    teams = Team.objects.all()
                    teams_data = []

                    for team in teams:
                        teams_data.append({'id': team.id, 'name': team.name, 'points': team.points()})

                    teams_data.sort(key=lambda x: x['points'], reverse=True)
                    current_state = json.dumps(teams_data)

                    if current_state != last_state:
                        yield f"data: {current_state}\n\n"
                        last_state = current_state
                        cache.delete('scoreboard_needs_update')

                time.sleep(1)

        response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response

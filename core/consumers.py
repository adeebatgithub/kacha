# consumers.py
import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.apps import apps
from django.db.models import Count, Q


class ScoreboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'scoreboard'

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Send initial data
        await self.send_initial_data()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        # Handle incoming messages if needed
        pass

    async def send_initial_data(self):
        """Send initial scoreboard data when client connects"""
        teams = await self.get_ranked_teams()
        recent_events = await self.get_recent_results()

        await self.send(text_data=json.dumps({'type': 'initial_data', 'teams': teams, 'recent_events': recent_events}))

    async def scoreboard_update(self, event):
        """Receive scoreboard update from group"""
        await self.send(text_data=json.dumps(event['data']))

    @database_sync_to_async
    def get_ranked_teams(self):
        Team = apps.get_model("core", "Team")
        teams = Team.objects.all()
        teams_with_points = []
        for team in teams:
            teams_with_points.append({'id': team.id, 'name': team.name, 'points': team.points})
        teams_with_points.sort(key=lambda x: x['points'], reverse=True)
        return teams_with_points

    @database_sync_to_async
    def get_recent_results(self):
        Event = apps.get_model("core", "Event")
        events = (Event.objects.annotate(
            podium_count=Count("results", filter=Q(results__position__in=[1, 2, 3]), distinct=True)).filter(
            podium_count=3).order_by("-id")[:5].prefetch_related("results"))

        results = []
        for event in events:
            first = event.results.filter(position=1).first()
            second = event.results.filter(position=2).first()
            third = event.results.filter(position=3).first()

            def get_first():
                if first.participant:
                    return first.participant.name.first_name
                return first.team.name

            def get_second():
                if second.participant:
                    return second.participant.name.first_name
                return second.team.name

            def get_third():
                if third.participant:
                    return third.participant.name.first_name
                return third.team.name

            results.append({'id': event.id, 'name': event.name, 'sub_category': event.get_sub_category_display(),
                            'first_place': {'participant': get_first(),
                                            'team': first.team.name if first else ''},
                            'second_place': {'participant': get_second()},
                            'third_place': {'participant': get_third()}})
        return results

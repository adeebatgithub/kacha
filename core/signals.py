# signals.py
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Team, Event, Result


def broadcast_scoreboard_update():
    """Broadcast scoreboard update to all connected clients"""
    channel_layer = get_channel_layer()

    # Get updated teams data
    teams = Team.objects.all()
    teams_with_points = []
    for team in teams:
        teams_with_points.append({'id': team.id, 'name': team.name, 'points': team.points})
    teams_with_points.sort(key=lambda x: x['points'], reverse=True)

    # Get recent events
    from django.db.models import Count, Q
    events = (Event.objects.annotate(
        podium_count=Count("results", filter=Q(results__position__in=[1, 2, 3]), distinct=True)).filter(
        podium_count=3).order_by("-id")[:5].prefetch_related("results"))

    recent_events = []
    for event in events:
        first = event.results.filter(position=1).first()
        second = event.results.filter(position=2).first()
        third = event.results.filter(position=3).first()
        print(second)

        def get_first():
            if first:
                if first.participant:
                    return first.participant.name.first_name
                return first.team.name

        def get_second():
            if second:
                if second.participant:
                    return second.participant.name.first_name
                return second.team.name

        def get_third():
            if third:
                if third.participant:
                    return third.participant.name.first_name
                return third.team.name

        recent_events.append({'id': event.id, 'name': event.name, 'sub_category': event.get_sub_category_display(),
            'first_place': {'participant': get_first(),
                'team': first.team.name if first else ''},
            'second_place': {'participant': get_second()},
            'third_place': {'participant': get_third()}})

    # Send to group
    async_to_sync(channel_layer.group_send)('scoreboard', {'type': 'scoreboard_update',
        'data': {'type': 'update', 'teams': teams_with_points, 'recent_events': recent_events}})


@receiver(post_save, sender=Team)
@receiver(post_save, sender=Result)
@receiver(post_delete, sender=Result)
def handle_scoreboard_change(sender, instance, **kwargs):
    """Trigger broadcast on any relevant model change"""
    broadcast_scoreboard_update()

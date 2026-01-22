from django.core.management import BaseCommand

from core.models import Result, Participant


class Command(BaseCommand):
    def handle(self, *args, **options):
        for result in Result.objects.all():
            if result.participant:
                part = Participant.objects.get(pk=result.participant.pk)
                part.points = 0
                part.save()
                part.points = part.points + (result.point + result.grade)
                part.save()
                self.stdout.write(f"{part.name.first_name} {part.points + (result.point + result.grade)}\n")

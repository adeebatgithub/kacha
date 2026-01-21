import re

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Team, Participant
from core.management.data import DATA


def normalize_username(name, chest_no):
    base = re.sub(r"[^a-zA-Z]", "", name).lower()
    return f"{base}{chest_no}" if base else f"user{chest_no}"


class Command(BaseCommand):
    help = "Seed teams, users, and participants"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Seeding data…")

        for team_name, members in DATA.items():
            # create a dummy captain if needed
            captain, _ = User.objects.get_or_create(
                username=f"{team_name.lower()}_captain",
                defaults={"password": "changeme123"},
            )

            team, created = Team.objects.get_or_create(
                name=team_name,
                defaults={
                    "captain": captain,
                    "vice_captain": captain,
                },
            )

            if created:
                self.stdout.write(f"Created team: {team_name}")

            for chest_no, name in members:
                if not name.strip():
                    continue

                username = normalize_username(name, chest_no)
                user, _ = User.objects.get_or_create(
                    username=username,
                    defaults={"first_name": name},
                )

                Participant.objects.get_or_create(
                    name=user,
                    team=team,
                    chest_no=chest_no,
                )

        self.stdout.write(self.style.SUCCESS("Seeding completed ✔"))

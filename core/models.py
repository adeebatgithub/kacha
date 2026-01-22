from django.contrib.auth import get_user_model
from django.db import models
from django.utils.functional import cached_property

from core.result.grade import GroupPoints, IndividualPoints, Grade

User = get_user_model()


class Event(models.Model):
    ON_STAGE = 1
    OFF_STAGE = 2
    CATEGORIES = ((ON_STAGE, 'On stage'), (OFF_STAGE, 'Off stage'),)
    GENERAL_GROUP = 1
    GENERAL_INDIVIDUAL = 2
    JUNIOR = 3
    SENIOR = 4
    SUB_CATEGORIES = ((GENERAL_GROUP, 'General group'), (GENERAL_INDIVIDUAL, 'General individual'), (JUNIOR, 'Junior'),
                      (SENIOR, 'Senior'),)
    name = models.CharField(max_length=100)
    category = models.PositiveSmallIntegerField(choices=CATEGORIES)
    sub_category = models.PositiveSmallIntegerField(choices=SUB_CATEGORIES)

    def __str__(self):
        return f"{self.name}({self.get_category_display()}-{self.get_sub_category_display()})"

    class Meta:
        ordering = ['-id']

    @cached_property
    def podium(self):
        return {r.position: r for r in self.results.all() if r.position in (1, 2, 3)}

    @property
    def first_place(self):
        return self.podium.get(1)

    @property
    def second_place(self):
        return self.podium.get(2)

    @property
    def third_place(self):
        return self.podium.get(3)


class Team(models.Model):
    name = models.CharField(max_length=100)
    captain = models.ForeignKey(User, on_delete=models.CASCADE, related_name='captain')
    vice_captain = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vice_captain')

    def __str__(self):
        return self.name

    @property
    def points(self):
        totals = Result.objects.filter(team=self).aggregate(points=models.Sum('point'), grade=models.Sum('grade'), )
        return (totals["points"] or 0) + (totals["grade"] or 0)

    def individual_points(self):
        totals = Result.objects.filter(team=self, participant__isnull=False).aggregate(points=models.Sum('point'),
                                                                                       grade=models.Sum('grade'), )
        return (totals["points"] or 0) + (totals["grade"] or 0)


class Participant(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    chest_no = models.IntegerField()
    points = models.IntegerField(default=0)

    def __str__(self):
        return self.name.username

    @property
    def total_points(self):
        totals = Result.objects.filter(participant=self).aggregate(points=models.Sum('point'), grade=models.Sum('grade'), )
        return (totals["points"] or 0) + (totals["grade"] or 0)


class Result(models.Model):
    POSITIONS = ((1, "First"), (2, "Second"), (3, "Third"),)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="results")
    position = models.PositiveSmallIntegerField(choices=POSITIONS, default=1)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, null=True, blank=True)
    point = models.IntegerField(default=0, null=True, blank=True)
    grade = models.IntegerField(default=0, choices=(
        (Grade.A, "A"), (Grade.B, "B"), (Grade.C, "C"), (Grade.D, "D"), (Grade.E, "E"))
                                )

    def save(self, *args, **kwargs):
        if self.event.sub_category == Event.GENERAL_GROUP:
            if self.position == 1:
                self.point = GroupPoints.First
            elif self.position == 2:
                self.point = GroupPoints.Second
            elif self.position == 3:
                self.point = GroupPoints.Third

        else:
            if self.position == 1:
                self.point = IndividualPoints.First
            elif self.position == 2:
                self.point = IndividualPoints.Second
            elif self.position == 3:
                self.point = IndividualPoints.Third

        if self.participant:
            self.participant.points += (self.point + self.grade)
            self.participant.save()

        return super().save(*args, **kwargs)

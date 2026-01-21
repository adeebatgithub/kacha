from django.contrib import admin

from core.models import *


@admin.register(Event)
class ModelNameAdmin(admin.ModelAdmin):
    pass


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    pass


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    pass



@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("event",)
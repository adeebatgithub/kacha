# views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import TeamForm, ParticipantFormSet
from core.models import Team


class TeamListView(LoginRequiredMixin, ListView):
    model = Team
    template_name = 'teams/team_list.html'
    context_object_name = 'teams'
    paginate_by = 10
    ordering = ['-id']


class TeamDetailView(LoginRequiredMixin, DetailView):
    model = Team
    template_name = 'teams/team_detail.html'
    context_object_name = 'team'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['participants'] = self.object.participant_set.all()
        return context


class TeamCreateView(LoginRequiredMixin, CreateView):
    model = Team
    form_class = TeamForm
    template_name = 'teams/team_form.html'
    success_url = reverse_lazy('team-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['participants'] = ParticipantFormSet(self.request.POST)
        else:
            context['participants'] = ParticipantFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        participants = context['participants']

        with transaction.atomic():
            self.object = form.save()
            if participants.is_valid():
                participants.instance = self.object
                participants.save()
            else:
                return self.form_invalid(form)

        return redirect(self.success_url)


class TeamUpdateView(LoginRequiredMixin, UpdateView):
    model = Team
    form_class = TeamForm
    template_name = 'teams/team_form.html'
    success_url = reverse_lazy('team-list')
    context_object_name = 'teams'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['participants'] = ParticipantFormSet(
                self.request.POST,
                instance=self.object,
                prefix='participants'
            )
        else:
            context['participants'] = ParticipantFormSet(
                instance=self.object,
                prefix='participants'
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        participants = context['participants']

        with transaction.atomic():
            self.object = form.save()
            if participants.is_valid():
                participants.instance = self.object
                participants.save()
            else:
                return self.form_invalid(form)

        return redirect(self.success_url)


class TeamDeleteView(LoginRequiredMixin, DeleteView):
    model = Team
    template_name = 'teams/team_confirm_delete.html'
    success_url = reverse_lazy('team-list')
    context_object_name = 'teams'

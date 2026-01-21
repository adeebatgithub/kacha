# views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (ListView, CreateView, UpdateView, DeleteView)

from core.models import Result
from .forms import ResultForm


class ResultListView(LoginRequiredMixin, ListView):
    model = Result
    template_name = "results/result_list.html"
    context_object_name = "results"


class ResultCreateView(LoginRequiredMixin, CreateView):
    model = Result
    form_class = ResultForm
    template_name = "results/result_form.html"
    success_url = reverse_lazy("result-list")

    def form_invalid(self, form):
        print(form.errors)


class ResultUpdateView(LoginRequiredMixin, UpdateView):
    model = Result
    fields = ["event", "position", "team", "participant", "point", "grade"]
    template_name = "results/result_form.html"
    success_url = reverse_lazy("result-list")


class ResultDeleteView(LoginRequiredMixin, DeleteView):
    model = Result
    success_url = reverse_lazy("result-list")

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().delete(request, *args, **kwargs)

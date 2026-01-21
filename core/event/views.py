from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from core.models import Event


class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 10
    ordering = ['-id']


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'


class EventCreateView(CreateView):
    model = Event
    template_name = 'events/event_form.html'
    fields = ['name', 'category', 'sub_category']
    success_url = reverse_lazy('event-list')

    def form_valid(self, form):
        return super().form_valid(form)


class EventUpdateView(UpdateView):
    model = Event
    template_name = 'events/event_form.html'
    fields = ['name', 'category', 'sub_category']
    success_url = reverse_lazy('event-list')
    context_object_name = 'event'


class EventDeleteView(DeleteView):
    model = Event
    template_name = 'events/event_confirm_delete.html'
    success_url = reverse_lazy('event-list')
    context_object_name = 'event'


    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().delete(request, *args, **kwargs)
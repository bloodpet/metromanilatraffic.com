#from django.views.generic import DetailView, ListView, CreateView, DeleteView, UpdateView
from django.views.generic import TemplateView, ListView
from core.models import *

class HomeView(TemplateView):
    northbound = Section.objects.filter(direction='n')
    southbound = Section.objects.filter(direction='s')
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        result = super(HomeView, self).get_context_data(**kwargs)
        result['northbound'] = self.northbound
        result['southbound'] = self.southbound
        return result

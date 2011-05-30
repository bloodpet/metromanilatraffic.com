#from django.views.generic import DetailView, ListView, CreateView, DeleteView, UpdateView
from django.views.generic import TemplateView, ListView, simple
from django.utils.decorators import method_decorator
from accounts.decorators import require_login
from core.models import *


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        result = super(HomeView, self).get_context_data(**kwargs)
        result['roads'] = Road.objects.all()
        result['ratings'] = TRAFFIC_RATINGS[1:]
        return result


class RoadView(TemplateView):
    template_name = 'road.html'

    def get_context_data(self, **kwargs):
        result = super(RoadView, self).get_context_data(**kwargs)
        road_slug = kwargs['road']
        result['ratings'] = TRAFFIC_RATINGS[1:]
        result['road'] = road = Road.objects.get(slug=road_slug)
        result['northbound'] = road.section_set.filter(direction='n')
        result['southbound'] = road.section_set.filter(direction='s')
        return result


class EditRoad(TemplateView):
    template_name = 'edit.html'

    @method_decorator(require_login)
    def dispatch(self, *args, **kwargs):
        return super(EditRoad, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        result = super(EditRoad, self).get_context_data(**kwargs)
        road_slug = kwargs['road']
        result['ratings'] = TRAFFIC_RATINGS[1:]
        result['road'] = road = Road.objects.get(slug=road_slug)
        result['northbound'] = road.section_set.filter(direction='n')
        result['southbound'] = road.section_set.filter(direction='s')
        return result

    def post(self, request, *args, **kwargs):
        for section in Section.objects.all():
            try:
                rating = request.POST['rate-%s' % section.id]
            except KeyError:
                continue
            else:
                situation = Situation.objects.create(section=section, rating=rating)
        return simple.redirect_to(request, request.path)

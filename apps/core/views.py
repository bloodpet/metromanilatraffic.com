import re
from django.core.urlresolvers import reverse
#from django.views.generic import DetailView, ListView, CreateView, DeleteView, UpdateView
from django.views.generic import TemplateView, ListView, simple
from django.utils.decorators import method_decorator
from django.contrib import messages
from accounts.decorators import require_login
from core.models import *
from core.backend import generate_sections

NONCAPS = re.compile('[^A-Z]')

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
        result['westbound'] = road.section_set.filter(direction='e')
        result['eastbound'] = road.section_set.filter(direction='w')
        return result


class EditRoad(TemplateView):
    template_name = 'edit.html'

    @method_decorator(require_login)
    def dispatch(self, *args, **kwargs):
        return super(EditRoad, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        result = super(EditRoad, self).get_context_data(**kwargs)
        road_slug = kwargs['road']
        ratings = []
        for rating in TRAFFIC_RATINGS[1:]:
            rating = (rating[0], NONCAPS.sub('', rating[1]))
            ratings.append(rating)
        result['ratings'] = ratings
        road = Road.objects.get(slug=road_slug)
        result['road_name'] = road.name
        result['northbound'] = road.section_set.filter(direction='n')
        result['southbound'] = road.section_set.filter(direction='s')
        result['westbound'] = road.section_set.filter(direction='e')
        result['eastbound'] = road.section_set.filter(direction='w')
        return result

    def post(self, request, *args, **kwargs):
        for section in Section.objects.all():
            try:
                rating = request.POST['rate-%s' % section.id]
            except KeyError:
                continue
            else:
                reason = request.POST.get('info-%s' % section.id, '')
                situation = Situation.objects.create(section=section, rating=rating, reason=reason)
                messages.success(self.request, 'Successfully posted update for %s.' % section.name)
        return simple.redirect_to(request, reverse('show_road', args=[kwargs['road'], ]))


class GenerateSections(TemplateView):
    template_name = 'generate_sections.html'

    @method_decorator(require_login)
    def dispatch(self, *args, **kwargs):
        return super(GenerateSections, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        result = super(GenerateSections, self).get_context_data(**kwargs)
        result['roads'] = Road.objects.all()
        return result

    def get(self, request, *args, **kwargs):
        if request.GET.has_key('slug'):
            road_slug = request.GET['slug']
            direction = request.GET['direction']
            road = Road.objects.get(slug=road_slug)
            generate_sections(road, direction)
            messages.success(self.request, 'Successfully created Sections')
            return simple.redirect_to(request, request.path_info)
        else:
            return super(GenerateSections, self).get(request, *args, **kwargs)

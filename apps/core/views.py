import re
from django.core.urlresolvers import reverse
#from django.views.generic import DetailView, ListView, CreateView, DeleteView, UpdateView
from django.views.generic import TemplateView, ListView, simple
from django.utils.decorators import method_decorator
from django.contrib import messages
from accounts.decorators import require_login
from core.models import *
from core.forms import *
from core.backend import generate_sections, get_statuses

NONCAPS = re.compile('[^A-Z]')
BASE_TEMPLATE = 'base.html'


class ThemeView(TemplateView):
    base_template = 'base.html'
    theme = None

    def get(self, request, *args, **kwargs):
        if 'theme' in request.GET:
            self.theme = request.GET['theme']
        return super(ThemeView, self).get(request, *args, **kwargs)

    def get_base_template(self):
        if self.theme is not None:
            return '%s/%s' % (self.theme, self.base_template)
        else:
            return self.base_template

    def get_context_data(self, **kwargs):
        result = super(ThemeView, self).get_context_data(**kwargs)
        result['base_template'] = self.get_base_template()
        result['theme'] = self.theme
        if self.theme is not None:
            result['section_template'] = '%s/%s' % (self.theme, 'section.html')
        else:
            result['section_template'] = 'section.html'
        return result

    def get_template_names(self):
        templates = []
        if self.theme is not False:
            templates.append('%s/%s' % (self.theme, self.template_name))
        templates.append(self.template_name)
        return templates


class MobileBase(object):

    def check_for_mobile(self, request):
        host_name = request.get_host()
        if host_name.startswith('m.') or host_name.startswith('mobile.'):
            self.is_mobile = True
            if not self.template_name.startswith('mobile'):
                self.template_name = 'mobile/' + self.template_name


class HomeView(ThemeView, MobileBase):
    template_name = 'home.html'

    def dispatch(self, request, *args, **kwargs):
        self.check_for_mobile(request)
        return super(HomeView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        result = super(HomeView, self).get_context_data(**kwargs)
        result['roads'] = Road.objects.annotate(latest_order=models.Max('section__situation__status_at')).order_by('-latest_order')
        result['ratings'] = TRAFFIC_RATINGS[3:]
        return result


class RoadView(ThemeView, MobileBase):
    template_name = 'road.html'

    def get(self, request, *args, **kwargs):
        self.check_for_mobile(request)
        if request.GET.has_key('d'):
            self.direction = request.GET['d']
        else:
            self.direction = None
        return super(RoadView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        result = super(RoadView, self).get_context_data(**kwargs)
        road_slug = kwargs['road']
        result['ratings'] = TRAFFIC_RATINGS[3:]
        result['road'] = road = Road.objects.get(slug=road_slug)
        result['northbound'] = road.section_set.filter(direction='n')
        result['southbound'] = road.section_set.filter(direction='s')
        result['westbound'] = road.section_set.filter(direction='e')
        result['eastbound'] = road.section_set.filter(direction='w')
        if self.direction:
            result['sections'] = road.section_set.filter(direction=self.direction)
            result['direction'] = DIRECTION_DICT[self.direction]
        return result


class EditRoad(ThemeView, MobileBase):
    template_name = 'edit.html'

    def get(self, request, *args, **kwargs):
        self.check_for_mobile(request)
        if request.GET.has_key('d'):
            self.direction = request.GET['d']
        else:
            self.direction = None
        return super(EditRoad, self).get(request, *args, **kwargs)

    @method_decorator(require_login)
    def dispatch(self, *args, **kwargs):
        return super(EditRoad, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        result = super(EditRoad, self).get_context_data(**kwargs)
        road_slug = kwargs['road']
        ratings = []
        for rating in TRAFFIC_RATINGS[3:]:
            rating = (rating[0], NONCAPS.sub('', rating[1]))
            ratings.append(rating)
        result['ratings'] = ratings
        road = Road.objects.get(slug=road_slug)
        result['road_name'] = road.name
        result['northbound'] = road.section_set.filter(direction='n')
        result['southbound'] = road.section_set.filter(direction='s')
        result['westbound'] = road.section_set.filter(direction='e')
        result['eastbound'] = road.section_set.filter(direction='w')
        if self.direction:
            result['road'] = road
            result['sections'] = road.section_set.filter(direction=self.direction)
            result['direction'] = DIRECTION_DICT[self.direction]
        # Try to get twitter updates if we have the correct libraries
        try:
            result['status_updates'] = get_statuses('MMDA', road_names=[road.name])
        except ImportError:
            pass
        return result

    def post(self, request, *args, **kwargs):
        for section in Section.objects.all():
            try:
                rating = request.POST['rate-%s' % section.id]
            except KeyError:
                continue
            else:
                reason = request.POST.get('info-%s' % section.id, '')
                situation = Situation.objects.create(
                    user=request.user,
                    is_from_user=True,
                    section=section,
                    rating=rating,
                    reason=reason
                )
                messages.success(self.request, 'Successfully posted update for %s.' % section.name)
        return simple.redirect_to(request, request.get_full_path())


class GenerateSections(ThemeView):
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


class CreateRoad(ThemeView, MobileBase):
    template_name = 'create-road.html'
    form_class = CreateRoadForm
    data = {}

    @method_decorator(require_login)
    def dispatch(self, *args, **kwargs):
        self.form = CreateRoadForm()
        return super(CreateRoad, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        result = super(CreateRoad, self).get_context_data(**kwargs)
        result['form'] = self.form
        return result

    def post(self, request, *args, **kwargs):
        form = self.form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(self.request, 'Successfully created new road')
            return simple.redirect_to(request, request.get_full_path())
        else:
            return super(CreateRoad, self).get(request, *args, **kwargs)

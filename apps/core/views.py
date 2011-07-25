import re
from django import http
from django.core.urlresolvers import reverse
#from django.views.generic import DetailView, ListView, CreateView, DeleteView, UpdateView
from django.views.generic import TemplateView, ListView, simple
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.utils import simplejson as json
from accounts.decorators import require_login
from core.models import *
from core.forms import *
from core.backend import generate_sections, get_statuses

NONCAPS = re.compile('[^A-Z]')
BASE_TEMPLATE = 'base.html'


class JSONResponseMixin(object):
    def render_to_response(self, context):
        "Returns a JSON response containing 'context' as payload"
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        "Construct an `HttpResponse` object."
        return http.HttpResponse(content,
                                 content_type='application/json',
                                 **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return json.dumps(context)


class ThemeView(TemplateView):
    base_template = 'base.html'
    theme = None

    def get(self, request, *args, **kwargs):
        data = request.GET.copy()
        data.update(kwargs)
        if 'theme' in data:
            self.theme = data['theme']
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


class HomeThemeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        base_template = 'base.html'
        theme = None
        result = super(HomeThemeView, self).get_context_data(**kwargs)
        if 'theme' in kwargs:
            theme = kwargs['theme']
            self.template_name = '%s/%s' % (theme, self.template_name)
        #result['roads'] = Road.objects.annotate(latest_order=models.Max('section__situation__status_at')).order_by('-latest_order')
        result['roads'] = Road.objects.all().order_by('pk')
        result['ratings'] = TRAFFIC_RATINGS[3:]
        result['theme'] = theme
        if theme is not None:
            result['section_template'] = '%s/%s' % (theme, 'section.html')
            result['base_template'] = '%s/%s' % (theme, base_template)
        else:
            result['section_template'] = 'section.html'
            result['base_template'] = base_template
        return result


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
        #result['roads'] = Road.objects.annotate(latest_order=models.Max('section__situation__status_at')).order_by('-latest_order')
        result['roads'] = Road.objects.all().order_by('pk')
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


class RoadSummary(JSONResponseMixin, TemplateView):
    queryset = Road.objects.all()

    def get_context_data(self, **kwargs):
        kwargs['roads'] = roads = []
        for entry in self.queryset:
            status = entry.get_latest_status()
            if status:
                latest = 'as of ' + status.status_at.strftime('%I:%m %p').strip('0').lower()
            else:
                latest = ''
            roads.append(dict(
                pk = entry.pk,
                latest_status = latest,
                average = entry.get_rate_average(),
            ))
        return TemplateView.get_context_data(self, **kwargs)

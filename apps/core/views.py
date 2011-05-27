#from django.views.generic import DetailView, ListView, CreateView, DeleteView, UpdateView
from django.views.generic import TemplateView, ListView
from django.utils.decorators import method_decorator
from accounts.decorators import require_login
from core.models import *


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        result = super(HomeView, self).get_context_data(**kwargs)
        result['northbound'] = Section.objects.filter(direction='n')
        result['southbound'] = Section.objects.filter(direction='s')
        result['ratings'] = TRAFFIC_RATINGS
        return result


class EditView(TemplateView):
    template_name = 'edit.html'

    @method_decorator(require_login)
    def dispatch(self, *args, **kwargs):
        return super(EditView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        result = super(EditView, self).get_context_data(**kwargs)
        result['northbound'] = Section.objects.filter(direction='n')
        result['southbound'] = Section.objects.filter(direction='s')
        result['ratings'] = TRAFFIC_RATINGS
        return result

    def post(self, request, *args, **kwargs):
        for section in Section.objects.all():
            try:
                rating = request.POST['rate-%s' % section.id]
            except KeyError:
                continue
            else:
                situation = Situation.objects.create(section=section, rating=rating)
        return super(EditView, self).get(request, *args, **kwargs)

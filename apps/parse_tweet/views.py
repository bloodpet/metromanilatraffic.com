# Create your views here.
from django.views.generic import TemplateView, simple
from django.utils.decorators import method_decorator
from django.contrib import messages
from accounts.decorators import require_login

class ParserView(TemplateView):
    template_name = 'parser.html'

    @method_decorator(require_login)
    def dispatch(self, *args, **kwargs):
        return super(ParserView, self).dispatch(*args, **kwargs)

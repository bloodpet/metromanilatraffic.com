# These are class-based generic views.
# You can read about the basic usage here: http://docs.djangoproject.com/en/1.3/topics/class-based-views/
# You can see the documentation here: http://docs.djangoproject.com/en/1.3/ref/class-based-views/
from django.views.generic import DetailView, ListView, CreateView, DeleteView, UpdateView
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from core.models import *
from core.generator.forms import *


class AliasListView(ListView):
    queryset = Alias.objects.all()
    template_name = 'generator/alias_list.html'
    context_object_name = 'alias_list'
    paginate_by = 10
    filters = {}

    def delete(self, alias):
        alias.delete()

    def get(self, request, *args, **kwargs):
        """Function for get requests."""
        search_class = AliasSearchForm
        if search_class._meta.fields:
            # Create search_form only if there are search fields
            if request.GET.get('action', '').lower() == 'search':
                self.search_form = search_class(request.GET)
                self.get_search_filters(request)
            else:
                self.search_form = search_class()
        else:
            self.search_form = None
        result = super(AliasListView, self).get(request, *args, **kwargs)
        return result

    def get_queryset(self):
        """Custom queryset for Alias."""
        queryset = super(AliasListView, self).get_queryset()
        return queryset.filter(**self.filters)

    def get_search_filters(self, request, *args, **kwargs):
        """Filter the queryset depending on the search parameters."""
        for k, v in request.GET.iteritems():
            if v and k in Alias._meta.get_all_field_names():
                if Alias._meta.get_field(k).get_internal_type() == 'CharField':
                    self.filters[k + '__contains'] = v
                else:
                    self.filters[k] = v
        return

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action', '')
        try:
            action_func = getattr(self, action)
        except AttributeError:
            pass
        else:
            alias_list = self.queryset.filter(pk__in=request.POST.getlist('alias'))
            for alias in alias_list:
                action_func(alias)
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Custom get_context_data to insert search form it the context."""
        result = super(AliasListView, self).get_context_data(**kwargs)
        result['search_form'] = self.search_form
        return result


class AliasDetailView(DetailView):
    queryset = Alias.objects.all()
    template_name = 'generator/alias_detail.html'
    context_object_name = 'alias'


class AliasCreateView(CreateView):
    model = Alias
    form_class = AliasForm
    template_name = 'generator/alias_create.html'
    context_object_name = 'alias'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AliasCreateView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, 'Successfully created Alias')
        return reverse('alias_show', args=[self.object.pk, ])


class AliasUpdateView(UpdateView):
    model = Alias
    form_class = AliasForm
    template_name = 'generator/alias_update.html'
    context_object_name = 'alias'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AliasUpdateView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, 'Successfully updated Alias')
        return reverse('alias_show', args=[self.object.pk, ])


class AliasDeleteView(DeleteView):
    model = Alias
    template_name = 'generator/alias_delete.html'
    context_object_name = 'alias'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AliasDeleteView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, 'Successfully deleted Alias')
        return reverse('alias_list')


class NodeListView(ListView):
    queryset = Node.objects.all()
    template_name = 'generator/node_list.html'
    context_object_name = 'node_list'
    paginate_by = 10
    filters = {}

    def delete(self, node):
        node.delete()

    def get(self, request, *args, **kwargs):
        """Function for get requests."""
        search_class = NodeSearchForm
        if search_class._meta.fields:
            # Create search_form only if there are search fields
            if request.GET.get('action', '').lower() == 'search':
                self.search_form = search_class(request.GET)
                self.get_search_filters(request)
            else:
                self.search_form = search_class()
        else:
            self.search_form = None
        result = super(NodeListView, self).get(request, *args, **kwargs)
        return result

    def get_queryset(self):
        """Custom queryset for Node."""
        queryset = super(NodeListView, self).get_queryset()
        return queryset.filter(**self.filters)

    def get_search_filters(self, request, *args, **kwargs):
        """Filter the queryset depending on the search parameters."""
        for k, v in request.GET.iteritems():
            if v and k in Node._meta.get_all_field_names():
                if Node._meta.get_field(k).get_internal_type() == 'CharField':
                    self.filters[k + '__contains'] = v
                else:
                    self.filters[k] = v
        return

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action', '')
        try:
            action_func = getattr(self, action)
        except AttributeError:
            pass
        else:
            node_list = self.queryset.filter(pk__in=request.POST.getlist('node'))
            for node in node_list:
                action_func(node)
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Custom get_context_data to insert search form it the context."""
        result = super(NodeListView, self).get_context_data(**kwargs)
        result['search_form'] = self.search_form
        return result


class NodeDetailView(DetailView):
    queryset = Node.objects.all()
    template_name = 'generator/node_detail.html'
    context_object_name = 'node'


class NodeCreateView(CreateView):
    model = Node
    form_class = NodeForm
    template_name = 'generator/node_create.html'
    context_object_name = 'node'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(NodeCreateView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, 'Successfully created Node')
        return reverse('node_show', args=[self.object.pk, ])


class NodeUpdateView(UpdateView):
    model = Node
    form_class = NodeForm
    template_name = 'generator/node_update.html'
    context_object_name = 'node'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(NodeUpdateView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, 'Successfully updated Node')
        return reverse('node_show', args=[self.object.pk, ])


class NodeDeleteView(DeleteView):
    model = Node
    template_name = 'generator/node_delete.html'
    context_object_name = 'node'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(NodeDeleteView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, 'Successfully deleted Node')
        return reverse('node_list')


class RoadListView(ListView):
    queryset = Road.objects.all()
    template_name = 'generator/road_list.html'
    context_object_name = 'road_list'
    paginate_by = 10
    filters = {}

    def delete(self, road):
        road.delete()

    def get(self, request, *args, **kwargs):
        """Function for get requests."""
        search_class = RoadSearchForm
        if search_class._meta.fields:
            # Create search_form only if there are search fields
            if request.GET.get('action', '').lower() == 'search':
                self.search_form = search_class(request.GET)
                self.get_search_filters(request)
            else:
                self.search_form = search_class()
        else:
            self.search_form = None
        result = super(RoadListView, self).get(request, *args, **kwargs)
        return result

    def get_queryset(self):
        """Custom queryset for Road."""
        queryset = super(RoadListView, self).get_queryset()
        return queryset.filter(**self.filters)

    def get_search_filters(self, request, *args, **kwargs):
        """Filter the queryset depending on the search parameters."""
        for k, v in request.GET.iteritems():
            if v and k in Road._meta.get_all_field_names():
                if Road._meta.get_field(k).get_internal_type() == 'CharField':
                    self.filters[k + '__contains'] = v
                else:
                    self.filters[k] = v
        return

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action', '')
        try:
            action_func = getattr(self, action)
        except AttributeError:
            pass
        else:
            road_list = self.queryset.filter(pk__in=request.POST.getlist('road'))
            for road in road_list:
                action_func(road)
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Custom get_context_data to insert search form it the context."""
        result = super(RoadListView, self).get_context_data(**kwargs)
        result['search_form'] = self.search_form
        return result


class RoadDetailView(DetailView):
    queryset = Road.objects.all()
    template_name = 'generator/road_detail.html'
    context_object_name = 'road'


class RoadCreateView(CreateView):
    model = Road
    form_class = RoadForm
    template_name = 'generator/road_create.html'
    context_object_name = 'road'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(RoadCreateView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, 'Successfully created Road')
        return reverse('road_show', args=[self.object.pk, ])


class RoadUpdateView(UpdateView):
    model = Road
    form_class = RoadForm
    template_name = 'generator/road_update.html'
    context_object_name = 'road'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(RoadUpdateView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, 'Successfully updated Road')
        return reverse('road_show', args=[self.object.pk, ])


class RoadDeleteView(DeleteView):
    model = Road
    template_name = 'generator/road_delete.html'
    context_object_name = 'road'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(RoadDeleteView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, 'Successfully deleted Road')
        return reverse('road_list')


class SectionListView(ListView):
    queryset = Section.objects.all()
    template_name = 'generator/section_list.html'
    context_object_name = 'section_list'
    paginate_by = 10
    filters = {}

    def delete(self, section):
        section.delete()

    def get(self, request, *args, **kwargs):
        """Function for get requests."""
        search_class = SectionSearchForm
        if search_class._meta.fields:
            # Create search_form only if there are search fields
            if request.GET.get('action', '').lower() == 'search':
                self.search_form = search_class(request.GET)
                self.get_search_filters(request)
            else:
                self.search_form = search_class()
        else:
            self.search_form = None
        result = super(SectionListView, self).get(request, *args, **kwargs)
        return result

    def get_queryset(self):
        """Custom queryset for Section."""
        queryset = super(SectionListView, self).get_queryset()
        return queryset.filter(**self.filters)

    def get_search_filters(self, request, *args, **kwargs):
        """Filter the queryset depending on the search parameters."""
        for k, v in request.GET.iteritems():
            if v and k in Section._meta.get_all_field_names():
                if Section._meta.get_field(k).get_internal_type() == 'CharField':
                    self.filters[k + '__contains'] = v
                else:
                    self.filters[k] = v
        return

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action', '')
        try:
            action_func = getattr(self, action)
        except AttributeError:
            pass
        else:
            section_list = self.queryset.filter(pk__in=request.POST.getlist('section'))
            for section in section_list:
                action_func(section)
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Custom get_context_data to insert search form it the context."""
        result = super(SectionListView, self).get_context_data(**kwargs)
        result['search_form'] = self.search_form
        return result


class SectionDetailView(DetailView):
    queryset = Section.objects.all()
    template_name = 'generator/section_detail.html'
    context_object_name = 'section'


class SectionCreateView(CreateView):
    model = Section
    form_class = SectionForm
    template_name = 'generator/section_create.html'
    context_object_name = 'section'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SectionCreateView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, 'Successfully created Section')
        return reverse('section_show', args=[self.object.pk, ])


class SectionUpdateView(UpdateView):
    model = Section
    form_class = SectionForm
    template_name = 'generator/section_update.html'
    context_object_name = 'section'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SectionUpdateView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, 'Successfully updated Section')
        return reverse('section_show', args=[self.object.pk, ])


class SectionDeleteView(DeleteView):
    model = Section
    template_name = 'generator/section_delete.html'
    context_object_name = 'section'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SectionDeleteView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, 'Successfully deleted Section')
        return reverse('section_list')


class SituationListView(ListView):
    queryset = Situation.objects.all()
    template_name = 'generator/situation_list.html'
    context_object_name = 'situation_list'
    paginate_by = 10
    filters = {}

    def delete(self, situation):
        situation.delete()

    def get(self, request, *args, **kwargs):
        """Function for get requests."""
        search_class = SituationSearchForm
        if search_class._meta.fields:
            # Create search_form only if there are search fields
            if request.GET.get('action', '').lower() == 'search':
                self.search_form = search_class(request.GET)
                self.get_search_filters(request)
            else:
                self.search_form = search_class()
        else:
            self.search_form = None
        result = super(SituationListView, self).get(request, *args, **kwargs)
        return result

    def get_queryset(self):
        """Custom queryset for Situation."""
        queryset = super(SituationListView, self).get_queryset()
        return queryset.filter(**self.filters)

    def get_search_filters(self, request, *args, **kwargs):
        """Filter the queryset depending on the search parameters."""
        for k, v in request.GET.iteritems():
            if v and k in Situation._meta.get_all_field_names():
                if Situation._meta.get_field(k).get_internal_type() == 'CharField':
                    self.filters[k + '__contains'] = v
                else:
                    self.filters[k] = v
        return

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action', '')
        try:
            action_func = getattr(self, action)
        except AttributeError:
            pass
        else:
            situation_list = self.queryset.filter(pk__in=request.POST.getlist('situation'))
            for situation in situation_list:
                action_func(situation)
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Custom get_context_data to insert search form it the context."""
        result = super(SituationListView, self).get_context_data(**kwargs)
        result['search_form'] = self.search_form
        return result


class SituationDetailView(DetailView):
    queryset = Situation.objects.all()
    template_name = 'generator/situation_detail.html'
    context_object_name = 'situation'


class SituationCreateView(CreateView):
    model = Situation
    form_class = SituationForm
    template_name = 'generator/situation_create.html'
    context_object_name = 'situation'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SituationCreateView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, 'Successfully created Situation')
        return reverse('situation_show', args=[self.object.pk, ])


class SituationUpdateView(UpdateView):
    model = Situation
    form_class = SituationForm
    template_name = 'generator/situation_update.html'
    context_object_name = 'situation'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SituationUpdateView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, 'Successfully updated Situation')
        return reverse('situation_show', args=[self.object.pk, ])


class SituationDeleteView(DeleteView):
    model = Situation
    template_name = 'generator/situation_delete.html'
    context_object_name = 'situation'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SituationDeleteView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, 'Successfully deleted Situation')
        return reverse('situation_list')


class UserListView(ListView):
    queryset = User.objects.all()
    template_name = 'generator/user_list.html'
    context_object_name = 'user_list'
    paginate_by = 10
    filters = {}

    def delete(self, user):
        user.delete()

    def get(self, request, *args, **kwargs):
        """Function for get requests."""
        search_class = UserSearchForm
        if search_class._meta.fields:
            # Create search_form only if there are search fields
            if request.GET.get('action', '').lower() == 'search':
                self.search_form = search_class(request.GET)
                self.get_search_filters(request)
            else:
                self.search_form = search_class()
        else:
            self.search_form = None
        result = super(UserListView, self).get(request, *args, **kwargs)
        return result

    def get_queryset(self):
        """Custom queryset for User."""
        queryset = super(UserListView, self).get_queryset()
        return queryset.filter(**self.filters)

    def get_search_filters(self, request, *args, **kwargs):
        """Filter the queryset depending on the search parameters."""
        for k, v in request.GET.iteritems():
            if v and k in User._meta.get_all_field_names():
                if User._meta.get_field(k).get_internal_type() == 'CharField':
                    self.filters[k + '__contains'] = v
                else:
                    self.filters[k] = v
        return

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action', '')
        try:
            action_func = getattr(self, action)
        except AttributeError:
            pass
        else:
            user_list = self.queryset.filter(pk__in=request.POST.getlist('user'))
            for user in user_list:
                action_func(user)
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Custom get_context_data to insert search form it the context."""
        result = super(UserListView, self).get_context_data(**kwargs)
        result['search_form'] = self.search_form
        return result


class UserDetailView(DetailView):
    queryset = User.objects.all()
    template_name = 'generator/user_detail.html'
    context_object_name = 'user'


class UserCreateView(CreateView):
    model = User
    form_class = UserForm
    template_name = 'generator/user_create.html'
    context_object_name = 'user'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserCreateView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, 'Successfully created User')
        return reverse('user_show', args=[self.object.pk, ])


class UserUpdateView(UpdateView):
    model = User
    form_class = UserForm
    template_name = 'generator/user_update.html'
    context_object_name = 'user'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserUpdateView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, 'Successfully updated User')
        return reverse('user_show', args=[self.object.pk, ])


class UserDeleteView(DeleteView):
    model = User
    template_name = 'generator/user_delete.html'
    context_object_name = 'user'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserDeleteView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, 'Successfully deleted User')
        return reverse('user_list')



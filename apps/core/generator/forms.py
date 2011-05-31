
import datetime
from django import forms

from core.models import *


class ContentForm(forms.ModelForm):

    def customize_fields(self):
        """Customize fields for content forms"""
        for field_name in self.fields:
            if isinstance(self.fields[field_name], (forms.CharField, )):
                self.fields[field_name].widget.attrs.update({
                    'class': 'txt-input',
                    'placeholder': self.fields[field_name].label,
                })
            elif isinstance(self.fields[field_name], (forms.DateField, forms.DateTimeField)):
                self.fields[field_name].widget.attrs.update({
                    'class': 'date-input',
                    'placeholder': self.fields[field_name].label,
                })
                self.fields[field_name].help_text = 'Format: YYYY-MM-DD (%s)' % datetime.datetime.now().strftime('%Y-%m-%d')
            elif isinstance(self.fields[field_name], forms.ChoiceField):
                self.fields[field_name].widget.attrs.update({
                    'class': 'dropdown',
                })
                self.fields[field_name].empty_label = '- %s -' % self.fields[field_name].label

class SearchForm(forms.ModelForm):

    def customize_fields(self, data):
        """Customize fields for the search forms"""
        for field_name in self.fields:
            if field_name in data.keys():
                self.fields[field_name].initial = data[field_name]
            if isinstance(self.fields[field_name], forms.CharField):
                if isinstance(self.fields[field_name].widget, forms.Textarea):
                    self.fields[field_name].widget = forms.TextInput()
                self.fields[field_name].widget.attrs.update({
                    'class': 'txt-input',
                    'placeholder': self.fields[field_name].label,
                })
            elif isinstance(self.fields[field_name], (forms.DateField, forms.DateTimeField)):
                self.fields[field_name].widget.attrs.update({
                    'class': 'date-input',
                    'placeholder': self.fields[field_name].label,
                })
            elif isinstance(self.fields[field_name], forms.ChoiceField):
                self.fields[field_name].widget.attrs.update({
                    'class': 'dropdown',
                })
                self.fields[field_name].empty_label = '- %s -' % self.fields[field_name].label


class NodeForm(ContentForm):
    class Meta:
        model = Node
        fields = ("road", "name", "latitude", "longitude", "position", )

    def __init__(self, *args, **kwargs):
        """Custom __init__ for NodeForm"""
        super(NodeForm, self).__init__(*args, **kwargs)
        self.customize_fields()


class NodeSearchForm(SearchForm):
    class Meta:
        model = Node
        fields = ("road", "name", "latitude", "longitude", "position", )

    def __init__(self, *args, **kwargs):
        """Custom __init__ for Node"""
        # Ignore the data
        args = list(args)
        try:
            data = args.pop(0)
        except IndexError:
            data = {}
        super(NodeSearchForm, self).__init__(*args, **kwargs)
        self.customize_fields(data)


class RoadForm(ContentForm):
    class Meta:
        model = Road
        fields = ("name", )

    def __init__(self, *args, **kwargs):
        """Custom __init__ for RoadForm"""
        super(RoadForm, self).__init__(*args, **kwargs)
        self.customize_fields()


class RoadSearchForm(SearchForm):
    class Meta:
        model = Road
        fields = ("name", )

    def __init__(self, *args, **kwargs):
        """Custom __init__ for Road"""
        # Ignore the data
        args = list(args)
        try:
            data = args.pop(0)
        except IndexError:
            data = {}
        super(RoadSearchForm, self).__init__(*args, **kwargs)
        self.customize_fields(data)


class SectionForm(ContentForm):
    class Meta:
        model = Section
        fields = ("road", "name", "start", "end", "direction", "position", )

    def __init__(self, *args, **kwargs):
        """Custom __init__ for SectionForm"""
        super(SectionForm, self).__init__(*args, **kwargs)
        self.customize_fields()


class SectionSearchForm(SearchForm):
    class Meta:
        model = Section
        fields = ("road", "name", "start", "end", "direction", "position", )

    def __init__(self, *args, **kwargs):
        """Custom __init__ for Section"""
        # Ignore the data
        args = list(args)
        try:
            data = args.pop(0)
        except IndexError:
            data = {}
        super(SectionSearchForm, self).__init__(*args, **kwargs)
        self.customize_fields(data)


class SituationForm(ContentForm):
    class Meta:
        model = Situation
        fields = ("section", "is_from_user", "rating", "reason", )

    def __init__(self, *args, **kwargs):
        """Custom __init__ for SituationForm"""
        super(SituationForm, self).__init__(*args, **kwargs)
        self.customize_fields()


class SituationSearchForm(SearchForm):
    class Meta:
        model = Situation
        fields = ("section", "is_from_user", "rating", "reason", )

    def __init__(self, *args, **kwargs):
        """Custom __init__ for Situation"""
        # Ignore the data
        args = list(args)
        try:
            data = args.pop(0)
        except IndexError:
            data = {}
        super(SituationSearchForm, self).__init__(*args, **kwargs)
        self.customize_fields(data)


class UserForm(ContentForm):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password", "is_staff", "is_active", "is_superuser", "last_login", "date_joined", )

    def __init__(self, *args, **kwargs):
        """Custom __init__ for UserForm"""
        super(UserForm, self).__init__(*args, **kwargs)
        self.customize_fields()


class UserSearchForm(SearchForm):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password", "is_staff", "is_active", "is_superuser", "last_login", "date_joined", )

    def __init__(self, *args, **kwargs):
        """Custom __init__ for User"""
        # Ignore the data
        args = list(args)
        try:
            data = args.pop(0)
        except IndexError:
            data = {}
        super(UserSearchForm, self).__init__(*args, **kwargs)
        self.customize_fields(data)


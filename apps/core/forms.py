from django import forms

from core.backend import generate_sections
from core.models import *

DIRECTIONS_CHOICES = [(d[0][0]+d[1][0], d[0][1]+'-'+d[1][1]) for d in DIRECTION_SETS]


class CreateRoadForm(forms.Form):
    name = forms.CharField(required=True)
    node_list = forms.CharField(
        widget=forms.Textarea,
        help_text='One node per line.'
    )
    directions = forms.ChoiceField(
        choices=DIRECTIONS_CHOICES,
        initial=DIRECTIONS_CHOICES[0][0],
    )

    def save(self, *args, **kwargs):
        road = Road.objects.create(name=self.cleaned_data['name'])
        nodes = self.cleaned_data['node_list'].split('\n')
        direction = self.cleaned_data['directions']
        for cnt, node_name in zip(range(len(nodes)), nodes):
            node = Node.objects.create(
                road = road,
                name = node_name,
                position = cnt,
            )
        generate_sections(road, direction)
        return road

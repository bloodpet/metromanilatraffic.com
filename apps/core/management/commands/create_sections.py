from optparse import make_option
from django.core.management.base import LabelCommand
from core.models import Road
from core.backend import generate_sections


class Command(LabelCommand):
    args = '<RoadSlug RoadSlug ...>'
    help = 'Create sections from the specified road slugs'
    option_list = LabelCommand.option_list + (
        make_option(
            '--direction', '-d',
            action = 'store',
            dest = 'direction',
            default = 'ns',
            help = 'Specify the direction of the road whether "ns" for north-south (and back) or "ew" for east-west (and back)',
        ),
    )

    def handle(self, *labels, **options):
        if not labels:
            labels = ['all',]
        if 'all' in labels:
            roads = Road.objects.all()
            result = ''
            for road in roads:
                result += generate_sections(road, options['direction'])
        else:
            result = super(Command, self).handle(*labels, **options)
        return result

    def handle_label(self, label, **options):
        try:
            road = Road.objects.get(slug=label)
        except Road.DoesNotExist:
            return "Road %s not found.\n" % label
        else:
            return generate_sections(road, options['direction'])

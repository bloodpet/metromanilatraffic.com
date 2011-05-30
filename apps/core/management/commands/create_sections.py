from optparse import make_option
from django.core.management.base import LabelCommand
from core.models import Road, Section


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
        self.direction = options['direction']
        if not labels:
            labels = ['all',]
        if 'all' in labels:
            roads = Road.objects.all()
            result = ''
            for road in roads:
                result += self.generate_sections(road)
        else:
            result = super(Command, self).handle(*labels, **options)
        return result

    def handle_label(self, label, **options):
        try:
            road = Road.objects.get(slug=label)
        except Road.DoesNotExist:
            return "Road %s not found.\n" % label
        else:
            return self.generate_sections(road)

    def generate_sections(self, road):
        if self.direction == 'ns':
            dir1 = 'n'
            dir2 = 's'
        else:
            dir1 = 'e'
            dir2 = 'w'
        nodes = road.node_set.all().order_by('position')
        node_count = nodes.count()
        for count, node1, node2 in zip(range(node_count), nodes[:node_count], nodes[1:]):
            section1 = road.section_set.create(name='%s to %s' % (node1.name, node2.name), start=node1, end=node2, direction=dir1, position=count)
            section1.save()
            section2 = road.section_set.create(name='%s to %s' % (node2.name, node1.name), start=node2, end=node1, direction=dir2, position=count)
            section2.save()
        return ''

from optparse import make_option
from django.core.management.base import NoArgsCommand
from tv5.parser import parse_site

class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option(
            '--roads',
            action = 'store',
            dest = 'roads',
            default = '',
            help = 'Specify roads to use',
        ),
    )

    def handle_noargs(self, **options):
        if options.get('roads'):
            road_slugs = options.get('roads', '').split(',')
        else:
            road_slugs = []
        verbosity = options['verbosity']
        results = parse_site(road_slugs, verbosity)
        return '\n'.join(['%s' % (result,) for result in results]) + '\n'

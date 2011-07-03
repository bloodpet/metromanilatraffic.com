from django.core.management.base import NoArgsCommand
from tv5.parser import parse_site

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        results = parse_site()
        return '\n'.join(['%s' % (result,) for result in results]) + '\n'

from django.core.management.base import NoArgsCommand
from core.models import Road
from parse_tweet.backend import get_statuses

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        results = []
        for road in Road.objects.all():
            results.append(str(get_statuses(road)))
        return '\n'.join(results)

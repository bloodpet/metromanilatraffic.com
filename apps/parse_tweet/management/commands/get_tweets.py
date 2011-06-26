from django.core.management.base import NoArgsCommand
from core.models import Road
from parse_tweet.parser import scrape_road

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        results = []
        for road in Road.objects.all():
            data = scrape_road(road)
            results.append('%s' % data)
        return '\n'.join(results)

from django.core.management.base import LabelCommand
from core.models import Road
from parse_tweet.backend import get_statuses

class Command(LabelCommand):

    def handle_label(self, label, **options):
        try:
            road = Road.objects.get(slug=label)
        except Road.DoesNotExist:
            return "Road %s not found.\n" % label
        else:
            return str(get_statuses(road))

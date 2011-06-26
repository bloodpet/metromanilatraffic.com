from django.core.management.base import NoArgsCommand
from parse_tweet.models import Tweet
from parse_tweet.parser import parse_entry

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        results = []
        for tweet in Tweet.objects.filter(is_parsed=False):
            results.append('%s' % parse_entry(tweet))
        return '\n'.join(results)

from django.core.management.base import NoArgsCommand
from parse_tweet.parser import parse_all_tweets

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        results = parse_all_tweets()
        return '\n'.join(['%s' for result in results])

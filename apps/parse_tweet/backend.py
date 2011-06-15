import re
from datetime import datetime
from BeautifulSoup import BeautifulSoup
from core.models import *
from parse_tweet.models import *

PATTERN_TIME = re.compile(r'.* ([1-9]*[0-9]+:[0-9][0-9])[ ]*([ap]m).*', re.IGNORECASE)
PATTERN_ALL = re.compile('')


class Parser(object):
    '''Parser - Read tweets to figure out traffic situation of a road

    20110615
    For now, this follows a strict format:
        for time, it should be written as: "as of %H:%M %p" (eg "as of 3:36 pm")
        for the update, it should be written as: "START to END - RATE" (eg "Magallanes to Ortigas - moderate to heavy")
    '''

    def __init__(self, road):
        self.road = road

    def get_candidates(self, part):
        for model in Node, Section:
            entries = model.objects.filter(road__id=self.road, name__iexact=part)
            if entries:
                return entries
            else:
                return model.objects.filter(road__id=self.road, alias__name__iexact=part)

    def get_sections(self, start_name, end_name):
        s = self.get_candidates(start_name)
        starts = None
        if s:
            if isinstance(s[0], Section):
                starts = s
            elif isinstance(s[0], Node):
                starts = Section.objects.filter(road__id=self.road, start=s[0])
        e = self.get_candidates(end_name)
        ends = None
        if e:
            if isinstance(e[0], Section):
                ends = e
            elif isinstance(e[0], Node):
                ends = Section.objects.filter(road__id=self.road, end=e[0])
        start, end = None, None
        if starts and ends:
            if starts.count() == 1 and ends.count() == 1:
                start, end = starts[0], ends[0]
            elif starts.count() >= 1 and ends.count() >= 1:
                # Test northbound & southbound
                for d in ('n', 's'):
                    try:
                        start_tmp = starts.get(direction=d)
                    except Section.DoesNotExist:
                        continue
                    try:
                        end_tmp = ends.get(direction=d)
                    except Section.DoesNotExist:
                        continue
                    if start_tmp.position <= end_tmp.position:
                        start, end = start_tmp, end_tmp
        if start and end:
            return Section.objects.filter(
                road__id = self.road,
                position__gte = start.position,
                position__lte = end.position,
                direction = start.direction,
            )
        return []

    def parse_range(self, txt, time):
        try:
            nodes, stat_alias = map(unicode.strip, txt.split('-'))
        except ValueError:
            return False
        start, end = map(unicode.strip, nodes.split(' to '))
        stat_alias = stat_alias.strip('.').strip('(').strip(')')
        stat = '"%s"' % stat_alias
        rate = 0
        for rate_tmp, aliases in zip(STAT_RATE, STAT_ALIASES):
            alias_str = '^(%s)$' % '|'.join(aliases)
            if re.match(alias_str, stat_alias, re.IGNORECASE):
                stat = aliases[0]
                rate = rate_tmp
        sections = self.get_sections(start, end)
        if rate > 0 and sections:
            # Update traffic situation on the sections
            for section in sections:
                situation = Situation.objects.create(
                    section = section,
                    rating = rate,
                    is_from_user = False,
                    status_at = time,
                )
                situation.save()
        sections_str = (unicode(section) for section in sections)
        #print '%s %s %s' % (rate, '"%s-%s"' % (start, end), ', '.join(sections_str))

    def parse_entry(self, entry):
        # Get time
        time = datetime.datetime.now()
        now = datetime.datetime.now()
        for full_txt in entry.fetchText(PATTERN_ALL):
            txt = full_txt.strip()
            if re.match('.*as of.*', txt, re.IGNORECASE):
                time_txt = PATTERN_TIME.sub('\\1 \\2', txt, re.IGNORECASE)
                try:
                    post_time = datetime.datetime.strptime(time_txt, '%H:%M %p')
                except ValueError:
                    # Ignore post if we can't recognize the time
                    return False
                post_hour = post_time.hour
                if time_txt.lower().find('pm') > -1:
                    if post_time.hour < 12:
                        post_hour = post_time.hour + 12
                # If the update is in the future, ignore it
                if post_hour > now.hour:
                    return False
                time = datetime.datetime(now.year, now.month, now.day, post_hour, post_time.minute)
        for full_txt in entry.fetchText(PATTERN_ALL):
            txt = full_txt.strip()
            if txt.startswith('@'):
                pass
            elif txt.startswith('#'):
                pass
            elif txt.find(' to ') > -1:
                for full_t in re.split('[;,]', txt):
                    t = full_t.strip()
                    if t.find(' to ') > -1:
                        self.parse_range(t, time)
        return


def parse_for_road(road, all_entries):
    now = datetime.datetime.now()
    parser = Parser(road.id)
    all_entries.reverse()
    for entry in all_entries:
        try:
            tweet = Tweet.objects.create(
                road = road,
                content = entry,
                is_parsed = False,
                updated_date = now.date,
            )
        except utils.IntegrityError:
            continue
        else:
            parser.parse_entry(entry)
            #tweet.save()

def get_statuses(road, twitter_name='MMDA', limit=5):
    '''A very basic twitter client to get traffic updates from MMDA by default.
    '''
    import httplib2
    now = datetime.datetime.now()
    since = now - datetime.timedelta(0, 120)
    h = httplib2.Http()
    tmp_url = 'http://search.twitter.com/search?&ors=%(road)s&lang=all&from=%(user)s&rpp=%(limit)i&%(since)s'
    url = tmp_url % dict(
        user = twitter_name,
        road = '+'.join(road.name),
        limit = limit,
        since = '%s-%s-%s' % (since.year, since.month, since.day),
    )
    try:
        resp, content = h.request(url, 'GET')
    except AttributeError, e:
        return []
    except httplib2.ServerNotFoundError, e:
        return []
    soup = BeautifulSoup(content)
    all_entries = soup.findAll('span', **{'class': re.compile('msgtxt.*')})
    parse_for_road(road, all_entries)
    entries = []
    for entry in all_entries:
        entries.append(''.join(entry.fetchText(PATTERN_ALL)))
    return entries

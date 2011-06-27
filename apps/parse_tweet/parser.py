# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# Tweet parser

import re
import datetime
import httplib2
from django.db import IntegrityError
from scrapemark import scrape    
from fuzzy import Soundex
from core.models import *
from parse_tweet.models import *

soundex = Soundex(6)

hours_ago = 2

patterns = dict(
    all = re.compile(''),
    ago = re.compile('[about ]*([0-9]*|half an?) ((hour|minute)s?) ago', re.IGNORECASE),
)

main_patterns = [
    'as of {{ time }}, {{ info }}; {{ section }}',
    'as of {{ time }}, {{ info }}: {{ section }}',
    'as of {{ time }}: {{ info }}: {{ section }}',
    'as of {{ time }}: {{ section }}',
    'as of {{ time }}, {{ section }}',
    '{{ info }}; {{ section }}',
    '{{ info }}: {{ section }}',
]

#TODO section_patterns: Fix these patterns to avoid separating Santolan to: San lan
section_patterns = [
    '{{ start }} to {{ end }}-{{ stat }}',
    '{{ start }} - {{ end }}({{ stat }})',
    '{{ start }}-{{ [stat] }} after {{ [stat] }} to {{ end }}',
    'approaching {{ stat }} to {{ end }}',
    'approaching {{ end }}-{{ stat }}',
    'after {{ stat }} to {{ end }}',
]


# Utilities

def download(url):
    h = httplib2.Http()
    #h = httplib2.Http('.cache')
    #print 'Downloading %s ...' % (url)
    resp, content = h.request(url, 'GET')
    #content = open('search.html').read()
    #content = open('search2.html').read()
    return content

def save_tweet(data):
    for datum in data:
        tweet = Tweet(
                **datum
            )
        try:
            tweet.save()
        except IntegrityError:
            pass
    return

def download_for_road(twitter_name, road, limit=10):
    since = datetime.datetime.utcnow() - datetime.timedelta(0, 60 * 60 * hours_ago)
    tmp_url = 'http://search.twitter.com/search?ors=&ands=%(road)s&lang=all&from=%(user)s&rpp=%(limit)i&since=%(since)s&time=%(time)s'
    url = tmp_url % dict(
        user = twitter_name,
        road = road.replace(' ', '+'),
        limit = limit,
        since = since.strftime('%Y-%m-%d'),
        time = since.strftime('%H:%M'),
    )
    return download(url)

def get_time(time):
    try:
        updated_at = datetime.datetime.strptime(time, '%b %d, %Y %H:%M %p %Z')
    except ValueError:
        #print 'Cannot parse %s' % time
        pass
    else:
        return updated_at
    if not patterns['ago'].search(time):
        # Assume that the data is one day old if the pattern is not recognized
        return now - datetime.timedelta(1, seconds)
    now = datetime.datetime.utcnow()
    days = 0
    seconds = 0
    value, unit = patterns['ago'].sub('\\1|\\2', time.lower()).split('|')
    if value.startswith('half a'):
        if unit.startswith('hour'):
            seconds = 30 * 60
        elif unit.startswith('minute'):
            seconds = 30
    else:
        try:
            ival = int(value)
        except ValueError:
            return None
        if unit.startswith('hour'):
            seconds = ival * 60 * 60
        elif unit.startswith('minute'):
            seconds = ival * 60
    updated_at = now - datetime.timedelta(days, seconds)
    return updated_at

def scrape_all(twitter_name='MMDA'):
    for road in Road.objects.all():
        data = scrape_road(road, twitter_name,)
        yield data


# Scrapemark specific methods

def scrape_road(road, twitter_name='MMDA'):
    html = download_for_road(twitter_name, road.name)
    tmp = '''{*
        <li class="result">
            <span id="msgtxt{{ [data].tweet_id }}" class="msgtxt">{{ [data].text }}</span>
            <div class="info">{{ [data].info }}<span /></div>
        </li>
    *}'''
    data = scrape(tmp, html)['data']
    for cnt in range(len(data)):
        if data[cnt]['info'].find('GMT') > -1:
            data[cnt]['info'] = re.sub('GMT.*', 'GMT', data[cnt]['info'])
        data[cnt]['updated_at'] = get_time(data[cnt]['info'])
        data[cnt]['road'] = road
        #data[cnt]['twitter_name'] = twitter_name
    save_tweet(data)
    return data


# Section specific methods

def parse_entry(entry):
    updated_at = entry.updated_at
    # Add 8 hours to consider Asia/Manila timezone
    #updated_at = updated_at + datetime.timedelta(0, 8 * 60 * 60)
    now = datetime.datetime.now()
    if updated_at.day > now.day:
        updated_at = updated_at - datetime.timedelta(1)
    text = entry.text
    text = re.sub('%s[, ]?' % entry.road.name, '', text, flags=re.IGNORECASE)
    text = re.sub('http://twitpic.com/[A-Za-z0-9] ?', '', text, flags=re.IGNORECASE)
    data = None
    # Figure out if the data would make sense.
    for main_pattern in main_patterns:
        test_data = scrape(main_pattern, text)
        if test_data is not None:
            data = test_data
            break
    if data is None:
        return
    # Get the time
    #print entry.road, updated_at.strftime('%d-%H:%M'),
    stat_time = data.get('time', None)
    if stat_time:
        if 'pm' in stat_time.lower():
            add12 = True
        else:
            add12 = False
        try:
            stat_time = datetime.datetime.strptime(stat_time.replace(' ', ''), '%H:%M%p')
        except KeyError, e:
            stat_time = updated_at
        except ValueError, e:
            #print stat_time.replace(' ', ''), e
            stat_time = updated_at
        if add12 and stat_time.hour < 12:
            stat_time = stat_time + datetime.timedelta(0, 12 * 60 * 60)
        actual_update = datetime.datetime(updated_at.year, updated_at.month, updated_at.day, stat_time.hour, stat_time.minute)
        # Correct the day if necessary
        if actual_update.day > updated_at.day:
            actual_update = actual_update - datetime.timedelta(1)
    else:
        actual_update = updated_at
    sections = re.sub('[. ]?[. ]?#mmda', '', data.get('section', '')).split(',')
    if sections:
        data_set = []
        for section in sections:
            section_data = parse_section(section)
            if 'stat' in section_data:
                rate = get_rate(section_data['stat'])
                if not rate:
                    continue
                road_sections = get_sections(section_data.get('start', ''), section_data.get('end', ''), entry)
                print rate, actual_update, updated_at, road_sections
                print section_data
                data_set.append(section_data)
                for road_section in road_sections:
                    situation = Situation(
                            section = road_section,
                            rating = rate,
                        )
                    situation.save()
                    situation.status_at = actual_update
                    situation.save()
                if road_sections:
                    entry.is_verified = True
            #print entry.road, section_data
    entry.is_parsed = True
    entry.save()
    return data_set

def parse_section(section):
    section_data = None
    for section_pattern in section_patterns:
        test_section_data = scrape(section_pattern, section)
        if test_section_data is not None:
            section_data = test_section_data
    if section_data is None:
        #print section
        return {}
        #return section
    recheck = False
    try:
        section_data['start']
    except KeyError:
        pass
    else:
        if ' to ' in section_data['start']:
            section_data['start'], section_data['end'] = section_data['start'].split(' to ')
        #TODO section_patterns: Fix the patterns above to avoid doing this hack
        if 'end' in section_data and \
                section_data['start'].lower().endswith('san') and \
                section_data['end'].lower().startswith('lan to '):
            section['start'] = 'Santolan'
            section['end'].lower().replace('lan to ', '')
    if isinstance(section_data['stat'], list):
        section_data['stat'] = '-'.join(section_data['stat'])
    is_saved = False
    if 'stat' not in section_data:
        #print section
        return {}
        #return section
    return section_data

def get_rate(stat):
    stat_alias = stat.lower()
    # Fix for some weird format by mmda
    # There has got to be a better way to do this!
    stat_alias = re.sub('\.\.\..*', '', stat_alias)
    for rate, aliases in zip(STAT_RATE, STAT_ALIASES):
        stat = None
        # First, find out if the given stat is in the alias list
        # This means that there are no typos.
        alias_str = '^(%s)$' % '|'.join(aliases)
        if re.match(alias_str.lower(), stat_alias.lower()):
            stat = aliases[0]
            print rate, aliases
            return rate
    for rate, aliases in zip(STAT_RATE, STAT_ALIASES):
        # If no match is found, try using soundex to find a match
        given = soundex(stat_alias)
        for alias in aliases:
            test = soundex(alias)
            if given == test:
                print rate, 'soundex', alias
                return rate
    print stat_alias, '-- NO RATE FOUND'

def get_sections(start, end, entry):
    start = re.sub('[neswNESW][bB][:;]? ?', '', start, re.IGNORECASE)
    end = re.sub('[neswNESW][bB][:;]? ?', '', end, re.IGNORECASE)
    direction = None
    if not start or not end:
        info = entry.info.lower()
        for abbrev, name in DIRECTIONS:
            if name in info or abbrev + 'b' in info:
                direction = abbrev
                break
    s_candidates = []
    e_candidates = []
    if start:
        s_candidates = get_section_candidates(start, entry.road, direction)
    if end:
        e_candidates = get_section_candidates(end, entry.road, direction)
    sections = []
    candidates = []
    section_q = Section.objects.filter(road=entry.road)
    if direction:
        section_q = section_q.filter(direction=direction)
    start_set = set()
    for sc in s_candidates:
        if isinstance(sc, Section):
            start_set.add(sc)
        else:
            sections = section_q.filter(start=sc)
            start_set.update(sections)
    end_set = set()
    for ec in e_candidates:
        if isinstance(ec, Section):
            end_set.add(ec)
        else:
            sections = section_q.filter(end=ec)
            end_set.update(sections)
    sections = set()
    for start_section in start_set:
        for end_section in end_set:
            if start_section.direction == end_section.direction and start_section.position <= end_section.position:
                sections.update(section_q.filter(
                    direction=start_section.direction,
                    position__gte=start_section.position,
                    position__lte=end_section.position,
                ))
    if direction and end_set and not start:
        # Figure out starting point
        #print end_set
        pass
    if direction and start_set and not end:
        # Figure out ending point
        #print start_set
        pass
    #if not sections:
        #print 'ROAD:%s START:%s END:%s ALL:%s' % (entry.road, start, end, entry.text)
    return sections


def get_section_candidates(name, road, direction):
    '''
    Try looking for candidates using ordinary queries.
    If that fails, use soundex.
    '''
    nq = Node.objects.filter(road=road)
    sq = Section.objects.filter(road=road)
    if direction:
        sq = sq.filter(direction=direction)
    for q in nq, sq:
        entries = q.filter(road=road, name__iexact=name)
        if entries:
            return entries
        entries_from_alias =  q.filter(road=road, alias__name__iexact=name)
        if entries:
            return entries
    entries = []
    try:
        name_snd = soundex(name)
    except UnicodeEncodeError:
        #TODO test this fix properly
        try:
            name_snd = soundex(name.encode('utf-8'))
        except Exception:
            print name
            return entries
    for q in nq, sq:
        for entry in q:
            try:
                entry_snd = soundex(entry.name)
            except UnicodeEncodeError:
                #TODO test this fix properly
                try:
                    entry_snd = soundex(entry.name.encode('utf-8'))
                except Exception:
                    continue
            if name_snd == entry_snd:
                entries.append(entry)
            else:
                for alias in entry.alias.all():
                    #TODO create a proper fix
                    try:
                        alias_snd = soundex(alias.name)
                    except UnicodeEncodeError:
                        #TODO test this fix properly
                        try:
                            alias_snd = soundex(alias.name.encode('utf-8'))
                        except Exception:
                            continue
                    if name_snd == alias_snd:
                        entries.append(entry)
                        break
    return entries


if __name__ == '__main__':
    for res in scrape_all():
        print res
    for tweet in Tweet.objects.filter(is_parsed=False):
        parse_entry(tweet)


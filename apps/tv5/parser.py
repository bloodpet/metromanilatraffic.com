# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# Interaksyon MMDA Traffic parser

import re
import datetime
import math
import httplib2
from django.db import IntegrityError
from scrapemark import scrape    
from fuzzy import Soundex
from core.models import Road, Situation

options = {}

soundex = Soundex(6)

patterns = [
    '''{*
        <div class="row-line{{ [line].row }}">
        <div class="line-name">
        <p>{{ [line].name }}</p>
        </div>
        <div class="line-col" align="center">
        <div id="{{ [line].stat_id1 }} " class="line-status {{ [line].status1 }}"></div>
        <p id="{{ [line].update_id1 }}">{{ [line].update_text1 }} ({{ [line].update_ago1 }})</p>
        </div>
        <div class="line-col" align="center">
        <div id="{{ [line].stat_id2 }}" class="line-status {{ [line].status2 }}"></div>
        <p id="{{ [line].update_id2 }}">{{ [line].update_text2 }} ({{ [line].update_ago2 }})</p>
        </div>
    *}''',
]

road_urls = [
    (1, ['edsa', ]),
    (6, ['quezon-ave', 'españa',]),
    (2, ['c5', ]),
    (4, ['roxas-blvd', ]),
    (5, ['slex', ]),
]

url_tmp = u'http://mmdatraffic.interaksyon.com/line-view-%s.php'

status_rate = dict(
    # Heavy
    ls1 = 7,
    ls4 = 7,
    ls5 = 7,
    ls6 = 7,
    # Light
    ls2 = 3,
    # Moderate
    ls3 = 5,
)

directions = {
    '1': ('s', 'w', ),
    '2': ('n', 'e', ),
}


class SectionStatus(object):
    d = {}

    def __unicode__(self):
        return u'%s' % self.d
    __repr__ = __unicode__

    def add(self, section, rate, time):
        if section not in self.d.keys():
            self.d[section] = {}
            self.d[section]['time'] = time
            self.d[section]['rates'] = []
        self.d[section]['rates'].append(rate)
        if self.d[section]['time'] < time:
            self.d[section]['time'] = time

    def get_middle(self, section):
        rates = self.d[section]['rates']
        rates.sort()
        mean = int(math.ceil( sum(rates) / float(len(rates)) ))
        #median = rates[int(math.ceil(len(rates)/2.0))]
        return mean

    def get_rates(self):
        if options['verbosity'] > 2:
            print self.d.keys()
        for section in self.d.keys():
            yield section, self.get_middle(section), self.d[section]['time']


class RoadParser(object):

    def __init__(self, road):
        self.lines = []
        self.section_status = SectionStatus()
        self.now = datetime.datetime.now()
        self.road = road

    def parse_line(self, line):
        now = datetime.datetime.now()
        for ind, dirs in directions.iteritems():
            rate = status_rate[line['status%s' % ind]]
            # figure out the direction of the sections
            for tmp_dir in dirs:
                if self.road.section_set.filter(direction=tmp_dir).count() > 0:
                    direction = tmp_dir
                    break
            name = line['name']
            #print name.encode('latin')
            # Get time
            update_ago = line['update_ago%s' % ind]
            value, unit, _ = update_ago.split(' ')
            if unit.find('hr') > -1:
                delta = datetime.timedelta(0, int(value) * 60 * 60)
            elif unit.find('min') > -1:
                delta = datetime.timedelta(0, int(value) * 60)
            elif unit.find('sec') > -1:
                delta = datetime.timedelta(0, int(value))
            else:
                if options['verbosity'] > 1:
                    print 'time not recognized'
                continue
            # Ignore updates 2 hrs ago
            if delta > datetime.timedelta(0, 2 * 60 * 60):
                if options['verbosity'] > 1:
                    print 'too old', delta, datetime.timedelta(0, 2 * 60 * 60)
                continue
            time = now - delta
            # Get sections & nodes
            nodes = set()
            nodes.update(self.road.node_set.filter(name__iexact=name), self.road.node_set.filter(alias__name__iexact=name))
            sections = set()
            section_query = self.road.section_set.filter(direction=direction)
            sections.update(section_query.filter(name__iexact=name), section_query.filter(alias__name__iexact=name))
            for node in nodes:
                sections.update(section_query.filter(start=node), section_query.filter(end=node))
            if sections:
                if options['verbosity'] > 2:
                    print rate, sections
                pass
            else:
                if options['verbosity'] > 1:
                    print 'No sections for', self.road.name, rate, name.encode('latin')
                pass
            for section in sections:
                if options['verbosity'] > 2:
                    print 'add to section_status', section, rate, time
                self.section_status.add(section, rate, time)

    def parse_lines(self):
        for line in self.lines:
            self.parse_line(line)

    def post_situations(self):
        situations = []
        for section, rate, time in self.section_status.get_rates():
            situation = Situation(
                section = section,
                rating = rate,
                reason = u'From MMDA Traffic',
                status_at = time,
            )
            situation.save()
            situation.status_at = time
            situation.save()
            if options['verbosity'] > 2:
                print (rate, time, section)
            situations.append(situation)
        return situations

    def scrape(self, content):
        self.content = content.decode('latin')
        for pattern in patterns:
            data = scrape(pattern, html=self.content)
            self.lines = self.lines + data['line']
        return self.lines


def parse_site(road_slugs, verbosity):
    options['verbosity'] = int(verbosity)
    #h = httplib2.Http()
    h = httplib2.Http('.cache')
    if road_slugs:
        roads = Road.objects.filter(slug__in=road_slugs)
    else:
        roads = Road.objects.all()
    for road_id, slugs in road_urls:
        road = Road.objects.get(id=road_id)
        if road not in roads:
            if options['verbosity'] > 1:
                print road, 'not in', roads, road_slugs
            continue
        parser = RoadParser(road)
        for slug in slugs:
            url = url_tmp % slug.decode('latin')
            resp, content = h.request(url, 'GET')
            parser.scrape(content)
            parser.parse_lines()
            situations = parser.post_situations()
            if situations:
                result = 'success', slug, situations
                if options['verbosity'] > 2:
                    print situations
                #result = '\n'.join('%s' % s for s in situations)
            else:
                result = 'None'
            yield result

if __name__ == '__main__':
    parse_site()

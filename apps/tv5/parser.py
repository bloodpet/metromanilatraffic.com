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
    #(6, ['quezon-ave', 'españa',]),
    #(2, ['c5', ]),
    #(4, ['roxas-blvd', ]),
    #(5, ['slex', ]),
]

url_tmp = u'http://mmdatraffic.interaksyon.com/line-view-%s.php'

status_rate = dict(
    # Heavy
    ls1 = 7,
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

    def add(self, section, rate):
        if section not in self.d.keys():
            self.d[section] = []
        self.d[section].append(rate)

    def get_middle(self, section):
        rates = self.d[section]
        rates.sort()
        mean = int(math.ceil( sum(rates) / float(len(rates)) ))
        #median = rates[int(math.ceil(len(rates)/2.0))]
        return mean

    def get_rates(self):
        for section in self.d.keys():
            yield section, self.get_middle(section)


class RoadParser(object):

    def __init__(self, road):
        self.lines = []
        self.section_status = SectionStatus()
        self.road = road

    def parse_line(self, line):
        for ind, dirs in directions.iteritems():
            rate = status_rate[line['status%s' % ind]]
            # figure out the direction of the sections
            for tmp_dir in dirs:
                if self.road.section_set.filter(direction=tmp_dir).count() > 0:
                    direction = tmp_dir
                    break
            # Get sections & nodes
            name = line['name']
            nodes = set()
            nodes.update(self.road.node_set.filter(name__iexact=name), self.road.node_set.filter(alias__name__iexact=name))
            sections = set()
            section_query = self.road.section_set.filter(direction=direction)
            sections.update(section_query.filter(name__iexact=name), section_query.filter(alias__name__iexact=name))
            for node in nodes:
                sections.update(section_query.filter(start=node), section_query.filter(end=node))
            if sections:
                #print rate, sections
                pass
            else:
                #print name
                pass
            for section in sections:
                self.section_status.add(section, rate)

    def parse_lines(self):
        for line in self.lines:
            self.parse_line(line)

    def post_situations(self):
        for section, rate in self.section_status.get_rates():
            situation = Situation(
                section = section,
                rating = rate,
                reason = u'From MMDA Traffic',
            )
            situation.save()

    def scrape(self, content):
        self.content = content
        for pattern in patterns:
            data = scrape(pattern, html=self.content)
            self.lines = self.lines + data['line']


def parse_site():
    #road = Road.objects.get(id=1)
    #parser = RoadParser(road)
    #content = open('line-view-edsa.php.htm').read()
    #parser.scrape(content)
    #parser.parse_lines()
    #parser.post_situations()
    ##print parser.section_status
    #return
    #h = httplib2.Http()
    h = httplib2.Http('.cache')
    for road_id, slugs in road_urls:
        road = Road.objects.get(id=road_id)
        parser = RoadParser(road)
        for slug in slugs:
            url = url_tmp % slug
            resp, content = h.request(url, 'GET')
            parser.scrape(content)
            parser.scrape(content)
            parser.parse_lines()
            result = parser.post_situations()
            yield result

if __name__ == '__main__':
    parse_site()

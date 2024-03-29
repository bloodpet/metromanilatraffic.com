import datetime
import math
from django.db import models
from django.template.defaultfilters import slugify

from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib import admin


DIRECTION_SETS = (
    (
        ('n', 'Northbound'),
        ('s', 'Southbound'),
    ),
    (
        ('e', 'Eastbound'),
        ('w', 'Westbound'),
    ),
)

DIRECTIONS = DIRECTION_SETS[0] + DIRECTION_SETS[1]
DIRECTION_DICT = dict(DIRECTIONS)

DIRECTIONS_CHOICES = [(d[0][0]+d[1][0], d[0][1]+'-'+d[1][1]) for d in DIRECTION_SETS]

# Number of hours to accept updates from
EARLIEST_HOUR = 3

TRAFFIC_RATINGS = (
    (0, 'No Update'),
    (1, 'Clear'),
    (2, 'Fast Moving'),
    (3, 'Light'),
    (4, 'Light - Moderate'),
    (5, 'Moderate'),
    (6, 'Moderate - Heavy'),
    (7, 'Heavy'),
    (8, 'Unpassable'),
)
TRAFFIC_DICT = dict(TRAFFIC_RATINGS)


class Alias(models.Model):
    '''Use alias to specify alternate names for roads, sections and nodes.
    '''
    name = models.CharField(max_length=128)
    content_type = models.ForeignKey(ContentType, related_name='alias', blank=True, null=True)
    object_id = models.PositiveIntegerField()
    orig = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name_plural = 'Aliases'

    def __unicode__(self):
        return self.name


class Road(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(unique=True, editable=False)
    alias = generic.GenericRelation(Alias)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('show_road', [self.slug, ])

    def get_directions(self):
        if self.section_set.latest('pk').direction in DIRECTIONS_CHOICES[1][0]:
            return DIRECTION_SETS[1]
        else:
            # Use the first choice by default
            return DIRECTION_SETS[0]

    def get_latest_status(self):
        try:
            latest_update = self.section_set.latest('situation__status_at').situation_set.latest('status_at')
        except models.exceptions.ObjectDoesNotExist:
            return False
        earliest_time = datetime.datetime.now() - datetime.timedelta(0, EARLIEST_HOUR * 60 * 60)
        if latest_update.status_at > earliest_time:
            return latest_update
        else:
            return None

    def get_rate_median(self):
        rates = []
        for section in self.section_set.all():
            try:
                rate_obj = section.get_latest_rate()
            except models.exceptions.ObjectDoesNotExist:
                continue
            rate = rate_obj.rating
            if rate > 0:
                rates.append(rate)
        # Get the upper median
        if len(rates) == 0:
            return None
        rates.sort()
        median = rates[len(rates)/2]
        return median

    def get_rate_mean(self):
        rates = []
        for section in self.section_set.all():
            try:
                rate_obj = section.get_latest_rate()
            except models.exceptions.ObjectDoesNotExist:
                continue
            rate = rate_obj.rating
            if rate > 0:
                rates.append(rate)
        # Get the upper mean
        if len(rates) == 0:
            return None
        mean = int(math.ceil( 1.0 * sum(rates) / len(rates) ))
        return mean

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super(Road, self).save(*args, **kwargs)

    get_rate_average = get_rate_mean

    # Directions:
    def northbound(self):
        return self.section_set.filter(direction='n')
    def southbound(self):
        return self.section_set.filter(direction='s')
    def eastbound(self):
        return self.section_set.filter(direction='e')
    def westbound(self):
        return self.section_set.filter(direction='w')


class Node(models.Model):
    road = models.ForeignKey(Road)
    name = models.CharField(max_length=128)
    latitude = models.FloatField(default=0, blank=True)
    longitude = models.FloatField(default=0, blank=True)
    position = models.SmallIntegerField()
    alias = generic.GenericRelation(Alias)

    class Meta:
        ordering = ['road', 'position', ]
        unique_together = ('road',  'position')

    def __unicode__(self):
        return '%s in %s' % (self.name, self.road.name)


class Section(models.Model):
    road = models.ForeignKey(Road)
    name = models.CharField(max_length=256)
    start = models.ForeignKey(Node, related_name='start_section')
    end = models.ForeignKey(Node, related_name='end_section')
    direction = models.CharField(max_length=1, choices=DIRECTIONS)
    position = models.PositiveSmallIntegerField()
    alias = generic.GenericRelation(Alias)
    latest_rating = models.SmallIntegerField(choices=TRAFFIC_RATINGS, default=0)
    latest_status_at = models.DateTimeField()

    class Meta:
        ordering = ['road', 'position', ]
        unique_together = (
            ('road', 'direction', 'position'),
            ('road', 'direction', 'start'),
            ('road', 'direction', 'end'),
        )

    def __unicode__(self):
        return '%s %s in %s' % (self.name, self.direction, self.road.name)

    def get_direction_name(self):
        return DIRECTION_DICT[direction]

    def get_latest_rate(self):
        latest_update = self.situation_set.latest('status_at')
        earliest_time = datetime.datetime.now() - datetime.timedelta(0, EARLIEST_HOUR * 60 * 60)
        if latest_update.status_at > earliest_time:
            return latest_update
        else:
            raise Situation.DoesNotExist

    def get_rate_name(self):
        return TRAFFIC_DICT[self.latest_rating]


class Situation(models.Model):
    section = models.ForeignKey(Section)
    user = models.ForeignKey(User, blank=True, null=True, editable=False)
    is_from_user = models.BooleanField(default=False)
    rating = models.SmallIntegerField(choices=TRAFFIC_RATINGS)
    updated_at = models.DateTimeField(auto_now_add=True)
    status_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True)

    def __unicode__(self):
        return '%s %s - %s' % (self.section, self.section.direction, self.rating)

    def get_rate_name(self):
        return TRAFFIC_DICT[self.rating]


class AliasInline(generic.GenericTabularInline):
    model = Alias

class MainAdmin(admin.ModelAdmin):
    inlines = [
            AliasInline,
        ]

class PartAdmin(MainAdmin):
    list_display = (
            '__unicode__',
            'road',
            'position',
        )

class NodeAdmin(PartAdmin):
    list_filter = (
            'road',
        )

class SectionAdmin(PartAdmin):
    list_filter = (
            'road',
            'direction',
        )

class StatAdmin(admin.ModelAdmin):
    list_display = (
            '__unicode__',
            'status_at',
            'updated_at',
        )


admin.site.register(Road, MainAdmin)
admin.site.register(Node, NodeAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Situation, StatAdmin)

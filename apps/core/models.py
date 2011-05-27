from django.db import models

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

TRAFFIC_RATINGS = (
    (1, 'Clear'),
    (2, 'Fast Moving'),
    (3, 'Light'),
    (4, 'Light to Moderate'),
    (5, 'Moderate'),
    (6, 'Moderate to Heavy'),
    (7, 'Heavy'),
    (8, 'Unpassable'),
)


class Road(models.Model):
    name = models.CharField(max_length=128)

    def __unicode__(self):
        return self.name


class Node(models.Model):
    road = models.ManyToManyField(Road)
    name = models.CharField(max_length=256)
    lattitude = models.IntegerField(default=0, blank=True)
    longitude = models.IntegerField(default=0, blank=True)

    def __unicode__(self):
        roads = self.road.all()
        if roads:
            return '%s in %s' % (self.name, ', '.join([road.name for road in roads]))
        else:
            return '%s' % (self.name)


class Section(models.Model):
    road = models.ManyToManyField(Road)
    name = models.CharField(max_length=128)
    start = models.ForeignKey(Node, related_name='start_section')
    end = models.ForeignKey(Node, related_name='end_section')
    direction = models.CharField(max_length=1, choices=DIRECTIONS)

    def __unicode__(self):
        roads = self.road.all()
        if roads:
            return '%s %s in %s' % (self.name, self.direction, ', '.join([road.name for road in roads]))
        else:
            return '%s %s' % (self.name, self.direction)

    def latest_rate(self):
        return self.situation_set.latest('id')


class Situation(models.Model):
    section = models.ForeignKey(Section)
    rating = models.SmallIntegerField(choices=TRAFFIC_RATINGS)
    updated_at = models.DateTimeField(auto_now_add=True)
    status_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s %s - %s' % (self.section, self.section.direction, self.rating)

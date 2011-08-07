"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


class RoadListTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

    def test_roads_by_pk(self):
        from core.models import Road, models
        return Road.objects.all().order_by('pk')

    def test_roads_by_update(self):
        from core.models import Road
        return Road.objects.annotate(latest_order=models.Max('section__situation__status_at')).order_by('-latest_order')


class RoadViewTest(TestCase):
    def test_road1(self):
        from core.models import Road
        road, new = Road.objects.get_or_create(name='EDSA')
        section_sets = [
            road.section_set.filter(direction='n'),
            road.section_set.filter(direction='s'),
            road.section_set.filter(direction='e'),
            road.section_set.filter(direction='w'),
        ]
        for section_set in section_sets:
            for section in section_set:
                print section.name, section.get_latest_rate().rating

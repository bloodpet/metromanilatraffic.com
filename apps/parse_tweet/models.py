from core.models import Road
from django.db import models
from django.db import utils
from django.contrib import admin

STAT_ALIASES = (
    ('l', 'light', 'fast moving', ),
    ('lm', 'ml', 'light-moderate', 'light - moderate', 'light to moderate', 'moderate-light', 'moderate - light', 'moderate to light',
        'fast-moderate', 'fast - moderate', 'fast to moderate', 'moderate-fast', 'moderate - fast', 'moderate to fast', ),
    ('m', 'moderate', ),
    ('mh', 'hm', 'heavy-moderate', 'heavy - moderate', 'heavy to moderate', 'moderate-heavy', 'moderate - heavy', 'moderate to heavy',
        'slow-moderate', 'slow - moderate', 'slow to moderate', 'moderate-slow', 'moderate - slow', 'moderate to slow', ),
    ('h', 'heavy', 'slow moving', ),
    ('u', 'unpassable', 'blocked', 'closed', ),
)
STAT_RATE = range(3, 9)


class Tweet(models.Model):
    tweet_id = models.IntegerField(unique=True)
    road = models.ForeignKey(Road)
    text = models.TextField()
    info = models.TextField()
    updated_at = models.DateTimeField(auto_now_add=True)
    status_at = models.DateTimeField(auto_now_add=True)
    is_parsed = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    class Meta:
        unique_together = (
            ('road', 'updated_at', 'text'),
        )

    def __unicode__(self):
        return self.text


class TweetAdmin(admin.ModelAdmin):
    list_display = ('road', 'status_at', 'updated_at', 'text', )
    list_filter = ('road', 'is_parsed', 'is_verified', )


admin.site.register(Tweet, TweetAdmin)

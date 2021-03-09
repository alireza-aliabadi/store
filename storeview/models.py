from django.db import models
from django.utils.translation import ugettext_lazy as _


# Create your models here.

class SlideShow(models.Model):
    title = models.CharField(_('title'), max_length=120)
    subtitle = models.CharField(_('subtitle'), max_length=300)
    image = models.ImageField(_('image'), upload_to='site/slideshow')
    action_title = models.CharField(_('action title'), max_length=20, default='shop now')
    action_url = models.URLField(_('action url'), default='', blank=True)

    def __str__(self):
        return self.title

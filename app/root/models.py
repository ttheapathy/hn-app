from django.db import models
from django.utils.translation import ugettext_lazy as _


class Post(models.Model):
    story_id = models.IntegerField(verbose_name=_('story id'), unique=True)
    title = models.CharField(verbose_name=_('story title'), max_length=255)
    url = models.URLField(verbose_name=_('story url'), max_length=255)
    created = models.DateTimeField(verbose_name=_('story created'), auto_now_add=True)

    class Meta:
        verbose_name = _('post')
        verbose_name_plural = _('posts')

    def __str__(self):
        return self.title

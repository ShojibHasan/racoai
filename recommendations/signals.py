from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from catalog.models import Category

from .services import clear_tree_cache


@receiver([post_save, post_delete], sender=Category)
def invalidate_category_tree(sender, **kwargs):
    # Any category change rebuilds the cached tree on next read
    clear_tree_cache()

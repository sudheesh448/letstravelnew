from django import template
from random import shuffle

register = template.Library()

@register.filter
def random_order(queryset):
    shuffled_list = list(queryset)
    shuffle(shuffled_list)
    return shuffled_list

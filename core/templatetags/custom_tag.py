from django import template
import uuid

from game.models import GameOrder

register = template.Library()

@register.filter(name="subtract")
def subtract(value, args):
    return f"{(float(value) - float(args)):.2f}"

@register.filter(name="percent_round")
def percent_round(value, args):
    return int((float(value) / float(args)) * 100)

@register.filter(name="range_in")
def range_in(value, args):
    return range(args, value)

@register.filter(name="unfilled_stars")
def unfilled_stars(value):
    return range(5 - value)

@register.filter(name="order_games_list")
def order_games_list(value):
    return value.games.all()
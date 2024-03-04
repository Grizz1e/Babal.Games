from django import template

register = template.Library()

@register.filter(name="subtract")
def subtract(value, args):
    return f"{(float(value) - float(args)):.2f}"

@register.filter(name="percent_round")
def percent_round(value, args):
    return int((float(value) / float(args)) * 100)
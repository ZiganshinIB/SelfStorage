from django import template
# from storage.models import Profile


register = template.Library()

@register.inclusion_tag('hello.html')
def example_include_tag():
    context = {
        'key': 'value',
    }
    return context





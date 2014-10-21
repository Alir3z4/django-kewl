from django import template
from django.utils.safestring import mark_safe


register = template.Library()


def meta_head(meta_property, sub_property, content):
    """
    :type meta_property: str
    :type sub_property: str
    :type content: str

    :rtype: str
    """
    return mark_safe(u'<meta '
                     u'property="{0}:{1}" '
                     u'content="{2}" />'.format(meta_property,
                                                sub_property,
                                                content))


@register.simple_tag
def meta_twitter(sub_property, content):
    """
    :type sub_property: str
    :type content: str

    :rtype: str
    """
    return meta_head('twitter', sub_property, content)


@register.simple_tag
def meta_open_graph(sub_property, content):
    """
    :type sub_property: str
    :type content: str

    :rtype: str
    """
    return meta_head('og', sub_property, content)

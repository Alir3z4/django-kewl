"""
Use these tags and filter when you're rolling your own search results.
This is intended to be a whole templatetags module. I keep it in my apps
 as templatetags/search.py. These should not be used to perform search
 queries, but rather render the results.

Basics
-------

There are three functions, each has both a tag and a filter of the same name.
 These functions accept, at a minimum, a body of text and a list of search terms:

searchexcerpt: Truncate the text so that each search term is shown,
surrounded by some number of words of context.
highlight: Wrap all found search terms in an HTML span that can be styled to
highlight the terms.

hits: Count the occurrences of the search terms in the text.
The filters provide the most basic functionality as described above, while the tags
offer more options as arguments, such as case sensitivity, whole word search, and
saving the results to a context variable.

Settings
---------
Defaults for both the tags and filters can be changed with the following
settings. Note that these settings are merely a convenience for the tags,
which accept
these as arguments, but are necessary for changing behavior of the filters.

* SEARCH_CONTEXT_WORDS: Number of words to show on the left and right of
each search term. Default: 10
* SEARCH_IGNORE_CASE: False for case sensitive, True otherwise. Default: True
* SEARCH_WORD_BOUNDARY: Find whole words and not strings in the middle of
words. Default: False
* SEARCH_HIGHLIGHT_CLASS: The class to give the HTML span element when
 wrapping highlighted search terms. Default: "highlight"

Examples
---------
Suppose you have a list flatpages resulting from a search query, and the
search terms (split into a list) are in the context variable terms. This will
show 5 words of context around each term and highlight matches in the title:

```
{% for page in flatpages %}
    <h3>{{ page.title|highlight:terms }}</h3>
    <p>
        {% searchexcerpt terms 5 %}
            {{ page.content|striptags }}
        {% endsearchexcerpt %}
    </p>
{% endfor %}
```
Add highlighting to the excerpt, and use a custom span class (the two flags
are for case insensitivity and respecting word boundaries):

```
{% highlight 1 1 "match" %}
{% searchexcerpt terms 5 1 1 %}
    {{ page.content|striptags }}
{% endsearchexcerpt %}
{% endhighlight %}
```
Show the number of hits in the body:
```
<h3>{{ page.title }}
    (Hits: {{ page.content|striptags|hits:terms }})
</h3>
```
All tags support an as name suffix, in which case an object will be stored in
the template context with the given name; output will be suppressed.
This is more efficient when you want both the excerpt and the number of hits.
The stored object depends on the tag:

* searchexcerpt: A dictionary with keys "original" (the text searched),
"excerpt" (the summarized text with search terms),
and "hits" (the number of hits in the text).
* searchcontext: A dictionary with keys "original", "highlighted", and "hits",
 with obvious values.
* hits: Just the number of hits, nothing special.

Getting both the hits and the excerpt with "as":
```
{% searchexcerpt terms 3 as content %}
    {{ page.content|striptags }}
{% endsearchexcerpt %}
<p>Hits: {{ content.hits }}<br>{{ content.excerpt }}</p>
```

More
----
For more examples see [Brian Beck's Text Adventure][1].

[1]: http://blog.brianbeck.com/post/29707610
"""
from itertools import ifilter
import re

from django import template
from django.conf import settings
from django.template import Node, TemplateSyntaxError
from django.utils.safestring import mark_safe


register = template.Library()

SETTINGS_PREFIX = 'SEARCH_'
SETTINGS_DEFAULTS = {
    'CONTEXT_WORDS': 10,
    'IGNORE_CASE': True,
    'WORD_BOUNDARY': False,
    'HIGHLIGHT_CLASS': "match"
}


def get_setting(name):
    return getattr(settings, SETTINGS_PREFIX + name, SETTINGS_DEFAULTS[name])


def searchexcerpt(text, phrases, context_words=None, ignore_case=None, word_boundary=None):
    if isinstance(phrases, basestring):
        phrases = [phrases]
    if context_words is None:
        context_words = get_setting('CONTEXT_WORDS')
    if ignore_case is None:
        ignore_case = get_setting('IGNORE_CASE')
    if word_boundary is None:
        word_boundary = get_setting('WORD_BOUNDARY')

    phrases = map(re.escape, phrases)
    flags = ignore_case and re.I or 0
    exprs = [re.compile(r"^%s$" % p, flags) for p in phrases]
    whitespace = re.compile(r'\s+')

    re_template = word_boundary and r"\b(%s)\b" or r"(%s)"
    pieces = re.compile(re_template % "|".join(phrases), flags).split(text)
    matches = {}
    word_lists = []
    index = {}
    for i, piece in enumerate(pieces):
        word_lists.append(whitespace.split(piece))
        if i % 2:
            index[i] = expr = ifilter(lambda e: e.match(piece), exprs).next()
            matches.setdefault(expr, []).append(i)

    def merge(lists):
        merged = []
        lists = [i for i in lists if i]

        for words in lists:
            if merged:
                merged[-1] += words[0]
                del words[0]
            merged.extend(words)

        return merged

    i = 0
    merged = []
    for j in map(min, matches.itervalues()):
        merged.append(merge(word_lists[i:j]))
        merged.append(word_lists[j])
        i = j + 1
    merged.append(merge(word_lists[i:]))

    output = []
    for i, words in enumerate(merged):
        omit = None
        if i == len(merged) - 1:
            omit = slice(max(1, 2 - i) * context_words + 1, None)
        elif i == 0:
            omit = slice(-context_words - 1)
        elif not i % 2:
            omit = slice(context_words + 1, -context_words - 1)
        if omit and words[omit]:
            words[omit] = ["..."]
        output.append(" ".join(words))

    return dict(original=text, excerpt="".join(output), hits=len(index))


class FunctionProxyNode(Node):
    def __init__(self, nodelist, args, variable_name=None):
        self.nodelist = nodelist
        self.args = args
        self.variable_name = variable_name

    def render(self, context):
        args = [arg.resolve(context) for arg in self.args]
        text = self.nodelist.render(context)
        value = self.get_value(text, *args)
        if self.variable_name:
            context[self.variable_name] = value
            return ""
        else:
            return self.string_value(value)

    def get_value(self, *args):
        raise NotImplementedError

    def string_value(self, value):
        return value


class SearchContextNode(FunctionProxyNode):
    def get_value(self, *args):
        return searchexcerpt(*args)

    def string_value(self, value):
        return value['excerpt']


@register.tag(name='searchexcerpt')
def searchexcerpt_tag(parser, token):
    """
        {% searchexcerpt search_terms [context_words] [ignore_case] [word_boundary] [as name] %}
        ...text...
        {% endsearchexcerpt %}
    """
    bits = list(token.split_contents())
    if not 3 <= len(bits) <= 8:
        usage = searchexcerpt_tag.__doc__.strip()
        raise TemplateSyntaxError("%r expected usage: %s" % (bits[0], usage))

    if len(bits) > 4 and bits[-2] == "as":
        args, name = bits[1:-2], bits[-1]
    else:
        args, name = bits[1:], None

    nodelist = parser.parse(('endsearchexcerpt',))
    parser.delete_first_token()
    return SearchContextNode(nodelist, map(parser.compile_filter, args), name)


@register.filter(name='searchexcerpt')
def searchexcerpt_filter(value, arg):
    return searchexcerpt(value, arg)['excerpt']


searchexcerpt_filter.is_safe = True


def highlight(text, phrases, ignore_case=None, word_boundary=None, class_name=None):
    if isinstance(phrases, basestring):
        phrases = [phrases]
    if ignore_case is None:
        ignore_case = get_setting('IGNORE_CASE')
    if word_boundary is None:
        word_boundary = get_setting('WORD_BOUNDARY')
    if class_name is None:
        class_name = get_setting('HIGHLIGHT_CLASS')

    phrases = map(re.escape, phrases)
    flags = ignore_case and re.I or 0
    re_template = word_boundary and r"\b(%s)\b" or r"(%s)"
    expr = re.compile(re_template % "|".join(phrases), flags)
    inner_expr = re.compile('<a[^>]+?href="[^>]*?(%s)$' % "|".join(phrases), flags)
    template = '<span class="%s">%%s</span>' % class_name
    matches = []

    def replace(match):
        if not word_boundary:
            span = match.span()
            if inner_expr.search(text, span[0] - 100, span[1]):
                return match.group(0)
        matches.append(match)

        return template % match.group(0)

    highlighted = mark_safe(expr.sub(replace, text))
    count = len(matches)

    return dict(original=text, highlighted=highlighted, hits=count)


class HighlightNode(FunctionProxyNode):
    def get_value(self, *args):
        return highlight(*args)

    def string_value(self, value):
        return value['highlighted']


@register.tag(name='highlight')
def highlight_tag(parser, token):
    """
        {% highlight search_terms [ignore_case] [word_boundary] [class_name] [as name] %}
        ...text...
        {% endhighlight %}
    """
    bits = list(token.split_contents())
    if not 2 <= len(bits) <= 7:
        usage = highlight_tag.__doc__.strip()
        raise TemplateSyntaxError("%r expected usage: %s" % (bits[0], usage))

    if len(bits) > 3 and bits[-2] == "as":
        args, name = bits[1:-2], bits[-1]
    else:
        args, name = bits[1:], None

    nodelist = parser.parse(('endhighlight',))
    parser.delete_first_token()
    return HighlightNode(nodelist, map(parser.compile_filter, args), name)


@register.filter(name='highlight')
def highlight_filter(value, arg):
    return highlight(value, arg)['highlighted']


def hits(text, phrases, ignore_case=None, word_boundary=None):
    if isinstance(phrases, basestring):
        phrases = [phrases]
    if ignore_case is None:
        ignore_case = get_setting('IGNORE_CASE')
    if word_boundary is None:
        word_boundary = get_setting('WORD_BOUNDARY')

    phrases = map(re.escape, phrases)
    flags = ignore_case and re.I or 0
    re_template = word_boundary and r"\b(%s)\b" or r"(%s)"
    expr = re.compile(re_template % "|".join(phrases), flags)
    return len(expr.findall(text))


class HitsNode(FunctionProxyNode):
    def get_value(self, *args):
        return hits(*args)

    def string_value(self, value):
        return "%d" % value


@register.tag(name='hits')
def hits_tag(parser, token):
    """
        {% hits search_terms [ignore_case] [word_boundary] [as name] %}
        ...text...
        {% endhits %}
    """
    bits = list(token.split_contents())
    if not 2 <= len(bits) <= 6:
        usage = hits_tag.__doc__.strip()
        raise TemplateSyntaxError("%r expected usage: %s" % (bits[0], usage))

    if len(bits) > 3 and bits[-2] == "as":
        args, name = bits[1:-2], bits[-1]
    else:
        args, name = bits[1:], None

    nodelist = parser.parse(('endhits',))
    parser.delete_first_token()
    return HitsNode(nodelist, map(parser.compile_filter, args), name)


@register.filter(name='hits')
def hits_filter(value, arg):
    return hits(value, arg)


hits.is_safe = True
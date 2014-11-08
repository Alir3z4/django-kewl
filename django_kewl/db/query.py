from django.core.paginator import Paginator


def queryset_iterator(queryset, chunk_size=23323):
    """
    Since Django normally loads all objects into its memory when iterating
    over a queryset (even with .iterator, although in that case it's not
    Django holding it in its memory, but your database client).

    ``queryset_iterator`` iterate over a given ``chunk_size`` and ``yield``
    the object.

    # Inspired by https://djangosnippets.org/snippets/1949/

    >>> from django.contrib.auth.models import User
    >>> from django_kewl.db.query import queryset_iterator
    >>>
    >>>
    >>> for user in queryset_iterator(User.objects.all()):
    >>>     user.send_latest_articles()
    >>>

    :type queryset: django.db.models.query.QuerySet
    :type per_page: int

    :rtype: collections.iterable
    """
    if not queryset:
        return

    last_row = queryset[queryset.count()-1]
    obj = None

    while last_row.pk != getattr(obj, 'pk', None):
        paginator = Paginator(queryset, chunk_size,
                              allow_empty_first_page=False)

        for page_number in paginator.page_range:
            page = paginator.page(page_number)

            for obj in page.object_list:
                yield obj


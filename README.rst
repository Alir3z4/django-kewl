===========
Django Kewl
===========

.. contents:: Table of contents

Overview
--------

`Django Kewl <ttps://github.com/Alir3z4/django-kewl/>`_ Set of Django kewl
utilities & helpers & highly used/needed stuff.

* `Template tags & filters <https://docs.djangoproject.com/en/dev/howto/custom-template-tags/>`_
* `Management Commands <https://docs.djangoproject.com/en/dev/howto/custom-management-commands/>`_
* Probably some other kewl stuff soon as well.


For now there only 3 kind of template tags implemented which will be more,
the current ones are:

* `search <https://github.com/Alir3z4/django-kewl/blob/master/django_kewl/templatetags/search.py>`_
    * ``searchexcerpt``
    * ``highlight``
    * ``hits``
* `meta_head <https://github.com/Alir3z4/django-kewl/blob/master/django_kewl/templatetags/meta_head.py>`_
    * ``meta_twitter``
    * ``meta_open_graph``
* `markwhat <https://github.com/Alir3z4/django-kewl/blob/master/django_kewl/templatetags/markwhat.py>`_
    * ``markdown``


Installation
------------
``django-kewl`` is available on pypi

http://pypi.python.org/pypi/django-kewl

So easily install it by ``pip``
::
    
    $ pip install django-kewl

Or by ``easy_install``
::
    
    $ easy_install django-kewl

Another way is by cloning ``django-kewl``'s `git repo <https://github.com/Alir3z4/django-kewl>`_ ::
    
    $ git clone git://github.com/Alir3z4/django-kewl.git

Then install it by running:
::
    
    $ python setup.py install


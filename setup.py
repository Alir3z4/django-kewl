from setuptools import setup

setup(
    name='django-kewl',
    version=".".join(map(str, __import__('short_url').__version__)),
    packages=['django_kewl'],
    url='https://github.com/Alir3z4/django-kewl',
    license='BSD',
    author='Alireza Savand',
    author_email='alireza.savand@gmail.com',
    description='Set of Django kewl utilities & helpers & highly used/needed stuff.',
    long_description=open('README.rst').read(),
)

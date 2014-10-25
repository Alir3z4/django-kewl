from setuptools import setup

setup(
    name='django-kewl',
    version=".".join(map(str, __import__('django_kewl').__version__)),
    packages=[
        'django_kewl',
        'django_kewl.templatetags',
    ],
    url='https://github.com/Alir3z4/django-kewl',
    license='BSD',
    author='Alireza Savand',
    author_email='alireza.savand@gmail.com',
    description='Set of Django kewl utilities & helpers & highly used/needed stuff.',
    long_description=open('README.rst').read(),
    platforms='OS Independent',
    install_requires=open('requirements.txt').read().splitlines(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development',
        'License :: OSI Approved :: BSD License',
    ],
)

import os
from setuptools import setup, find_packages


def read_file(filename):
    """Read a file into a string"""
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    try:
        return open(filepath).read()
    except IOError:
        return ''


setup(
    name='django-sendgrid-webhook',
    version=__import__('sendgrid').__version__,
    author='Jann Kleen',
    author_email='jann.kleen@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/resmio/django-sendgrid',
    license='BSD 2-Clause',
    description=' '.join(__import__('sendgrid').__doc__.splitlines()).strip(),
    classifiers=[
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
    ],
    long_description=read_file('README.md'),
    test_suite='runtests.run_tests',
    zip_safe=False,
)

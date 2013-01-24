from setuptools import setup, find_packages


kwargs = {
    'packages': find_packages(exclude=['tests', '*.tests', '*.tests.*', 'tests.*']),
    'include_package_data': True,

    'install_requires': ['django', 'django-guardian'],

    'test_suite': 'test_suite',

    'name': 'django-governor',
    'version': __import__('governor').get_version(),
    'author': 'Byron Ruth',
    'author_email': 'b@devel.io',
    'description': '',
    'license': 'BSD',
    'keywords': 'object permissions django guardian',
    'url': 'http://bruth.github.com/django-governor/',
    'classifiers': [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
        'Intended Audience :: Developers',
    ],
}

setup(**kwargs)

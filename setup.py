from setuptools import find_packages
from setuptools import setup


setup(
    name='sandglass.time',
    version='0.1.0',
    packages=find_packages(),
    namespace_packages=['sandglass'],
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'gunicorn',
        'pyramid==1.5',
        'pyramid_tm==0.7',
        'pyramid_mailer==0.13',
        'sqlalchemy==0.9.1',
        'alembic==0.6.3',
        'zope.sqlalchemy',
        'zope.component==4.1.0',
        # Enum support for python < 3.4
        'flufl.enum',
        # Forms/data handling
        'colander',
        # Translations extraction support
        'Babel',
        'lingua',
        # Documentation support
        'Sphinx',
        # Timezone support
        'pytz',
        # Command line support
        'cement',
        'PasteScript',
    ],
    entry_points={
        'paste.app_factory': [
            'main = sandglass.time.main:make_wsgi_app',
        ],
        'console_scripts': [
            'sandglass = sandglass.time.command:main',
        ],
    },
    paster_plugins=['pyramid'],
    message_extractors={
        'sandglass/time': [
            ('**.py', 'lingua_python', None),
            ('tests/**', 'ignore', None),
            ('locales/**', 'ignore', None),
        ],
    },
)

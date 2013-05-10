from distutils.core import setup

setup(
    name='Emergence',
    version='0.0.0',
    author='Joshua Orvis',
    author_email='jorvis@gmail.com',
    packages=['emergence', 'emergence.test'],
    scripts=[],
    url='http://code.google.com/p/emergence/',
    license='LICENSE.txt',
    description='A biological sequence annotation and analysis system.',
    long_description=open('README.txt').read(),
    install_requires=[
        "Django >= 1.6",
        "django-celery >= 3.0.19",
)

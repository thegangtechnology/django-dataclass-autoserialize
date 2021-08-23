from os.path import join, dirname

from setuptools import setup, find_packages


def get_version():
    fname = join(dirname(__file__), "src/django_dataclass_autoserialize/__version__.py")
    with open(fname) as f:
        ldict = {}
        code = f.read()
        exec(code, globals(), ldict)  # version defined here
        return ldict['version']


package_name = "django_dataclass_autoserialize"

setup(name=package_name,
      version=get_version(),
      description='',
      long_description=open('README.md').read().strip(),
      long_description_content_type='text/markdown',
      author='Piti Ongmongkolkul',
      author_email='o.piti@thegang.tech',
      url='https://github.com/thegangtechnology/django-dataclass-autoserialize',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      py_modules=[package_name],
      install_requires=[
          # it's currrently need tiny patch to dataclass serializer
          'djangorestframework-dataclasses',
          'drf-yasg'
      ],
      extras_require={
          'dev': [
              'mypy',
              'autopep8',
              'pytest',
              'pytest-cov'
          ]
      },
      license='BSD',
      zip_safe=False,
      keywords='',
      classifiers=[''],
      package_data={
          package_name: ['py.typed'],
      }
      )

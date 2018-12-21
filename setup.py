from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='pycdaac',
      version='0.1',
      description='CDAAC data download program provided by Haitao Liu',
      long_description=readme(),
      classifiers=[
          'Development Status :: 1 - Alpha',
          'License :: OSI Approved :: Apache License 2.0',
          'Programming Language :: Python :: 3.6',
          'Topic :: Data process :: Space Physics, Ionosphere',
      ],
      keywords='python CDAAC download',
      url='https://github.com/htyeim/pycdaac',
      author='Haitao Liu',
      author_email='htyeim@gmail.com',
      license='MIT',
      install_requires=[
          'numpy',
          'scipy',
          'pandas',
          'matplotlib',
          'pygc',
          'netCDF4',
          'astropy',
          'obspy',
          'cartopy',
      ],
      packages=['pycdaac'],
      include_package_data=True,
      entry_points={
          'console_scripts': ['pycdaac-joke=pycdaac.command_line:main'],
      },
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)

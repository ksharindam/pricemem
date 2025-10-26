from setuptools import setup
import platform
from pricemem import __version__, AUTHOR_NAME, AUTHOR_EMAIL

def readme():
    with open('README.md') as f:
        return f.read()

if platform.system()=='Linux':
    data_files = [('share/applications', ['data/pricemem.desktop']),
                ('share/icons/hicolor/scalable/apps', ['data/icons/pricemem.png'])]
else:
    data_files = []

setup(
    name='pricemem',
    version=__version__,
    description='Product price management tool for small shops',
    long_description=readme(),
    long_description_content_type = 'text/markdown',
    keywords='price',
    url='http://github.com/ksharindam/pricemem',
    author=AUTHOR_NAME,
    author_email=AUTHOR_EMAIL,
    license='GNU GPLv3',
    #install_requires=['PyQt5',],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: X11 Applications :: Qt',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3',
    ],
    packages=['pricemem'],
    entry_points={
      'gui_scripts': ['pricemem=pricemem.main:main'],
    },
    data_files = data_files,
    include_package_data=True,
    zip_safe=False
    )

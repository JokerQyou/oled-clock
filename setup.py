# coding: utf-8
from setuptools import setup

__version__ = '0.1.0'

setup(
    name='oled_clock',
    version=__version__,
    license='BSD',
    author='Joker Qyou',
    description='A simple clock for SSD1306 OLED screen',
    packages=['oled_clock', ],
    include_package_data=True,
    zip_safe=False,
    platforms='linux2',
    install_requires=open('requirements.txt').readlines(),
    entry_points='''
        [console_scripts]
        oclock=oled_clock.cli:start_daemon
    '''
)

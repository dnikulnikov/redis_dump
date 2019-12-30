from os.path import join, dirname
import sys
from setuptools import setup, find_packages


CURRENT_DIR = join(dirname(__file__))
PY_VER = sys.version_info


if PY_VER < (3, 6):
    raise RuntimeError("amocrm doesn't suppport Python earlier than 3.5")


def get_long_description():
    with open(join(CURRENT_DIR, 'README.md'), 'r') as f:
        return f.read()


def get_requirements():
    res = []
    with open(join(CURRENT_DIR, 'requirements.txt'), 'r') as f:
        res = f.read().split("\n")
        res = list(filter(lambda x: x, res))
    return res


setup(
    name='redis-dump',
    license='MIT',
    version='1.0.0',
    maintainer='Nikulnikov Denis',
    maintainer_email='denic-nik@mail.ru',
    url='https://github.com/',
    description='Redis dump utily.',
    long_description=get_long_description(),
    packages=find_packages(),
    entry_points={'console_scripts': [
        'redis-dump=redis_dump:main'
    ]},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Russian',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.7',
    ],
    install_requires=get_requirements(),
)

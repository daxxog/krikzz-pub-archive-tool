from setuptools import setup, find_packages


requirements = [
    "requests",
    "beautifulsoup4"
]


with open('README.rst') as f:
    long_desc = f.read()

with open('VERSION') as f:
    version = f.read()


setup(
    name='krikzz-pub-archive-tool',
    version=version,
    description='Tool for backing up: http://krikzz.com/pub/',
    long_description=long_desc,
    author='David Volm',
    author_email='david@volminator.com',
    url='https://github.com/daxxog/krikzz-pub-archive-tool',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.9',
        'Topic :: System :: Archiving :: Backup',
        'Topic :: System :: Archiving :: Mirroring'
    ],
    license='Apache 2.0',
    install_requires=requirements,
    py_modules=['krikzz_pub_archive_tool'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'krikzz-pub-archive-tool = krikzz_pub_archive_tool:main',
        ],
    },
)


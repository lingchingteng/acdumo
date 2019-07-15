import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='acdumo',
    version='0.0.1',
    author='Anthony Aylward, Serena Wu, Elijah Kun',
    author_email='aaylward@eng.ucsd.edu',
    description='Accelerated dual momentum',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/anthony-aylward/acdumo',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    entry_points = {'console_scripts': ['acdumo=acdumo.acdumo:main']}
)
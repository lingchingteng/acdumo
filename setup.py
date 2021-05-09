import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='acdumo',
    version='1.1.0',
    author='Anthony Aylward, Serena Wu, Elijah Kun',
    author_email='aaylward@eng.ucsd.edu',
    description='Accelerated dual momentum',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/anthony-aylward/acdumo',
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires = [
        'email-validator',
        'flask',
        'flask-apscheduler',
        'flask-login',
        'flask-mail',
        'flask-migrate',
        'flask-misaka',
        'flask-wtf',
        'pyjwt',
        'misaka',
        'pandas',
        'seaborn',
        'wtforms',
        'yahoofinancials',
    ],
    entry_points = {
        'console_scripts': [
            'acdumo=acdumo.acdumo:main',
            'acdumo-install-certifi=acdumo.install_certifi:main'
        ]
    }
)

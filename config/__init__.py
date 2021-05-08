#!/user/bin/env python3
#===============================================================================
# config
#===============================================================================

"""Create a config file"""




# Imports ======================================================================

import argparse
import os
import os.path




# Constants ====================================================================

DEVELOPMENT_CONFIG_DATA = f'''
import os
import os.path
basedir = os.path.abspath(os.path.dirname(__file__))
SECRET_KEY = os.environ.get('SECRET_KEY') or {os.urandom(16)}
SQLALCHEMY_DATABASE_URI = (
    os.environ.get('DATABASE_URL')
    or 'sqlite:///' + os.path.join(basedir, 'app.db')
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
PROTECTED_DIR = os.path.join(basedir, 'protected')
MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = ''
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
ADMINS = ['anthony.aylward@protonmail.com']
APPROVED_EMAILS = ['anthony.aylward@protonmail.com']
'''

PRODUCTION_CONFIG_DATA = f'''
import os
import os.path
basedir = os.path.abspath(os.path.dirname(__file__))
SECRET_KEY = os.environ.get('SECRET_KEY') or {os.urandom(16)}
SQLALCHEMY_DATABASE_URI = (
    os.environ.get('DATABASE_URL')
    or 'sqlite:///' + os.path.join(basedir, 'app.db')
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
PROTECTED_DIR = os.path.join(basedir, 'protected')
MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'mail.smtp2go.com'
MAIL_PORT = int(os.environ.get('MAIL_PORT') or 465)
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'accelerated.dual.momentum@acdumo.info'
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
ADMINS = ['accelerated.dual.momentum@acdumo.info']
APPROVED_EMAILS = [
    'anthony.aylward@protonmail.com',
    'green.danying@gmail.com',
    'craylward@gmail.com',
    'elijahwaichunkun@gmail.com',
    'work@lbry.com'
]
'''




# Functions ====================================================================

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='write configuration file'
    )
    parser.add_argument(
        'instance',
        metavar='<path/to/instance-folder/>',
        help='path to instance folder'
    )
    parser.add_argument(
        '--production',
        action='store_true',
        help='write a production config file'
    )
    return parser.parse_args()

def main():
    args = parse_arguments()
    with open(os.path.join(args.instance, 'config.py'), 'w') as f:
        f.write(
            PRODUCTION_CONFIG_DATA if args.production
            else DEVELOPMENT_CONFIG_DATA
        )




# Execute ======================================================================

if __name__ == '__main__':
    main()

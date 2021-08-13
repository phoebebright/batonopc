#!/bin/bash

set -e 
DJANGO_HOME_DIR=$( dirname $(dirname $(readlink -e $0) ) )
PROJECT_NAME=$(basename $DJANGO_HOME_DIR)
VENV_NAME=${1:-$PROJECT_NAME}

setup_ansible() {
    ansible-galaxy install -f -p roles -r requirements.yml 
    ansible-playbook playbook.yml  #--extra-vars "@configs/$PROJECT_NAME.yml"
} 


setup_django() {
    cd $1
    export DJANGO_SETTINGS_MODULE=config.settings
    source /home/django/virtualenvs/$VENV_NAME/bin/activate
    set -x
    python manage.py check
    python manage.py collectstatic --noinput
} 

setup_ansible 
setup_django $DJANGO_HOME_DIR  

#!/bin/bash

set -e
set -o pipefail
export LC_ALL=C

export ANSIBLE_VAR_NGINX_LE_ACCOUNT=${ANSIBLE_VAR_NGINX_LE_ACCOUNT:-ben@bom.org.uk}

eval "$( curl -s  https://gitlab.com/Rubanau/cloud-tools/raw/master/envvars_check.sh )"

# do variables check
# in case it's first thing to be deployed
envvars_check_abort_if_missing ANSIBLE_VAR_BACKUPS_SPACES_BUCKET    \
                               ANSIBLE_VAR_BACKUPS_SPACES_AWS_ACCESS_KEY    \
                               ANSIBLE_VAR_BACKUPS_SPACES_AWS_SECRET_ACCESS_KEY 

envvars_check_warn_if_missing   ANSIBLE_VAR_PAPERTRAIL_DESTINATION      \
                                ANSIBLE_VAR_BACKUPS_SPACES_REGION
                                

export ANSIBLE_VAR_NGINX_LE_PRIMARY_DOMAIN=$( curl -s http://169.254.169.254/metadata/v1/hostname )
export ANSIBLE_VAR_NGINX_LE_MODE=${ANSIBLE_VAR_NGINX_LE_MODE:-prod}
export ANSIBLE_VAR_NGINX_LE_BRAVE_MODE=${ANSIBLE_VAR_NGINX_LE_BRAVE_MODE:-yes}
ANSIBLE_VAR_NGINX_LE_IMAGE_DEFAULT=hleb/nginx-letsencrypted:1.2.4-vts
export ANSIBLE_VAR_NGINX_LE_IMAGE_ID=${ANSIBLE_VAR_NGINX_LE_IMAGE_ID:-$ANSIBLE_VAR_NGINX_LE_IMAGE_DEFAULT}


export ANSIBLE_VAR_NGINX_LE_LOGGING_OPTIONS_INLINE='"tag: nginx"'

envvars_check_report   \
                        ANSIBLE_VAR_NGINX_LE_PRIMARY_DOMAIN \
                        ANSIBLE_VAR_NGINX_LE_ACCOUNT        \
                        ANSIBLE_VAR_NGINX_LE_MODE           \
                        ANSIBLE_VAR_NGINX_LE_IMAGE_ID       \
                        ANSIBLE_VAR_BACKUPS_SPACES_BUCKET   \
                        ANSIBLE_VAR_BACKUPS_SPACES_REGION   \
                        ANSIBLE_VAR_GADGETS_DOMAIN          


set -x
curl -s https://gitlab.com/Rubanau/cloud-tools/raw/master/ssh_validate_git_providers_fingerprints.sh | /bin/bash | tee -a /etc/ssh/ssh_known_hosts
curl -s https://gitlab.com/Rubanau/cloud-tools/raw/master/install_ansible_apt.sh | /bin/bash
curl -s https://gitlab.com/Rubanau/cloud-tools/raw/master/configure_local_ansible.sh | /bin/bash
set +x

export DEPLOYMENT_GIT_UPSTREAM=git@github.com:phoebebright/batonopc.git
export DEPLOYMENT_GIT_WORKDIR=/home/django/batonopc
export DEPLOYMENT_GIT_SUBDIR=devops
export DEPLOYMENT_COMMAND='./setup.sh'
curl -s https://raw.githubusercontent.com/hleb-rubanau/ansible-role-deploy-via-git-pull/master/bootstrap.sh | /bin/bash

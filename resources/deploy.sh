#!/usr/bin/env bash 
# Script that is executed on the production system to deploy the new code
# I'm not sure if there's a better way to do so, but this works
#

HDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/../ >/dev/null 2>&1 && pwd )"
echo "HYDRA_HOME=$HDIR" | sudo tee /etc/sysconfig/hydra-notifierd >/dev/null
UNIT_FILE=hydra-notifierd.service
UNIT_DIR=/etc/systemd/system
cd $HDIR
git pull || exit 1
rm -rf .venv || exit 1
python3.6 -m virtualenv .venv || exit 1
. .venv/bin/activate || exit 1
pip3.6 install -r requirements.txt || exit 1
(sudo cp -p ${HDIR}/resources/$UNIT_FILE $UNIT_DIR && sudo sed -i 's;HYDRA_HOME;'"$HDIR"';g'  ${UNIT_DIR}/$UNIT_FILE && sudo sudo systemctl daemon-reload) || exit 1
if ! sudo systemctl is-enabled $UNIT_FILE --quiet;then sudo systemctl enable $UNIT_FILE || exit 1;fi
alembic revision --autogenerate -m "init"
alembic upgrade head
sudo systemctl restart $UNIT_FILE || exit 1

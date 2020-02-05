#!/bin/bash 
MARIADB_SERVICE_HOST=$(echo "${INSTANCE_NAME}-MARIADB-SERVICE-HOST" | sed 's/-/_/g' | tr "[a-z]" "[A-Z]")
while ! echo > /dev/tcp/${!MARIADB_SERVICE_HOST}/3306; do
  echo "Rundeck still not up"
  sleep 10
done
alembic revision --autogenerate -m "${OPENSHIFT_BUILD_NAME} ${OPENSHIFT_BUILD_REFERENCE} ${OPENSHIFT_BUILD_COMMIT}"
alembic upgrade head

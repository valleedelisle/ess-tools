#!/bin/bash 
alembic revision --autogenerate -m "${OPENSHIFT_BUILD_NAME} ${OPENSHIFT_BUILD_REFERENCE} ${OPENSHIFT_BUILD_COMMIT}"
alembic upgrade head

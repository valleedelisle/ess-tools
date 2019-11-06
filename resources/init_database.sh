#!/bin/bash 
alembic revision --autogenerate -m "${OPENSHIFT_BUILD_COMMIT}"
alembic upgrade head

#!/bin/bash 
alembic revision --autogenerate -m "${1:-init}"
alembic upgrade head

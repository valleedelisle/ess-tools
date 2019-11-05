#!/bin/bash
oc delete all --all
oc delete persistentvolumeclaims  --all 
oc delete secret/ess-notifier-mariadb-persistent 

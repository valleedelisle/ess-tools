#!/bin/bash
oc delete all -l app=ess-notifier
oc delete persistentvolumeclaims  -l app=ess-notifier
oc delete secret/ess-notifier

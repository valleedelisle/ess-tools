#!/bin/bash
oc delete all -l set=review-auto-dump
oc delete persistentvolumeclaims  -l set=review-auto-dump
oc delete secret/review-auto-dump
oc delete secret/gitlab-webhook-secret

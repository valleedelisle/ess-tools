[![pipeline status](https://gitlab.cee.redhat.com/dvalleed/ess-tools/badges/master/pipeline.svg)](https://gitlab.cee.redhat.com/dvalleed/ess-tools/commits/master)
[![Build Status](https://travis-ci.com/valleedelisle/ess-tools.svg?branch=master)](https://travis-ci.com/valleedelisle/ess-tools)

# Table of Contents
1. [Description](#description)
2. [Events](#events)
3. [Installation](#installation)
4. [Author](#author)

## Description

This repository contains a set of tool to interact with the [Hydra API](https://mojo.redhat.com/groups/cee-integration/blog/2016/12/06/hydra-rest-api), a Red Hat internal API mapped to the case application.

### Notifierd
The notification tool will poke the API every X seconds based on a set of configuration and criteria. Some events will trigger notifications.

#### Notification type
- SMS (using [Twilio](https://www.twilio.com/))
- Mail (using [Mailgun](https://www.mailgun.com/)) or using a standard SMTP
- Logfile

#### Events
This is the list of events that will trigger a notification:
- Severity change
- RME is activated
- Case is escalated
- Critical Situation is activated
- Customer Escalation
- FTS (24x7) is activated
- SBT is breached, or nearly breached, it's customizable
- New case in Queue

### Case closer
Tool that takes a list of cases and closes them

### Case tagger
Tool that takes a list of cases and adds tags to them

### Event Report
Tool that generates an email with the last events for specific accounts. It's good for handover across timezone.

### Bug Report
Tool that generates a report of the open bugs for specific accounts and feeds an [Airtable](https://airtable)
```
bug-report.py --customer NAME-OF-CUSTOMER --get-bz
```

Make sure you filled the `airtable` and `bugzilla` configuration and that you have a `base_id` defined in the `customer`'s section.


## Installation

- Clone this repository
```
$ git clone git@github.com:valleedelisle/ess-tools.git
```
- To send email notification, you need to have a [Mailgun](https://www.mailgun.com/) account or you need to have access to an SMTP server.
- To send SMS notification, you need to have a [Twilio](https://www.twilio.com) account.
- You can add the secrets, customer list, passwords and api_key in `hydra-notifierd-secrets.conf`
- Add the secret files to the openshift secrets
```
oc create secret generic ess-notifier-config --from-file hydra-notifierd-secrets.conf --from-file service-account.json
```
- Generate a JWT token to save in an environment variable
```
$ export JWT_REFRESH_TOKEN=$(curl -s -d "username=$RHN_USER&password=$RHN_PASS&grant_type=password&client_id=hydra-client-cli" https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token | jq -r '.refresh_token')
```
- Deploy the app
```
$ oc new-app openshift/templates/python-mariadb-persistent.yaml --name notifier -e JWT_REFRESH_TOKEN=$JWT_REFRESH_TOKEN
```

- To cleanup the deploy, you can use the `delete_oc_resource.sh` script
```
$ ./resources/delete_oc_resources.sh 
pod "ess-notifier-mariadb-persistent-1-build" deleted
pod "ess-notifier-mariadb-persistent-1-ghhmf" deleted
pod "mariadb-1-zw2xm" deleted
replicationcontroller "ess-notifier-mariadb-persistent-1" deleted
replicationcontroller "mariadb-1" deleted
service "mariadb" deleted
deploymentconfig.apps.openshift.io "ess-notifier-mariadb-persistent" deleted
deploymentconfig.apps.openshift.io "mariadb" deleted
buildconfig.build.openshift.io "ess-notifier-mariadb-persistent" deleted
imagestream.image.openshift.io "ess-notifier-mariadb-persistent" deleted
persistentvolumeclaim "mariadb" deleted
secret "ess-notifier-mariadb-persistent" deleted
```

## TODO
- Complete automatic reporting of events twice per day
- Autorebuild on commit

## Author
David Vallee Delisle <dvd@redhat.com>

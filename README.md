[![pipeline status](https://gitlab.cee.redhat.com/dvalleed/hydra-notifierd/badges/master/pipeline.svg)](https://gitlab.cee.redhat.com/dvalleed/hydra-notifierd/commits/master)

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

#### Case closer
Tool that takes a list of cases and closes them

#### Case tagger
Tool that takes a list of cases and adds tags to them

#### Report
Tool that generates an email with the last events for specific accounts. It's good for handover across timezone.

## Installation

- Clone this repository

```
$ git clone git@github.com:valleedelisle/hydra-notifierd.git
```

- To send email notification, you need to have a [Mailgun](https://www.mailgun.com/) account or you need to have access to an SMTP server.

- To send SMS notification, you need to have a [Twilio](https://www.twilio.com) account.

- Build a venv

```
$ virtualenv-3 .venv
```

- Install requirements

```
$ pip3 install -r requirements.txt
```

- Edit `hydra-notifierd.conf`

- You can add the secrets and password in `hydra-notifierd-secrets.conf`

- Execute the `hydra-notifierd.py` script after loading the venv

```
$ source .venv/bin/activate
$ ./hydra-notifierd.py
```

- Add a key to `authorized_keys` for automated deploy
```
command="/git/hydra-notifier/resources/deploy.sh",no-port-forwarding,no-x11-forwarding,no-agent-forwarding ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBEknEO6tjWf7rX7ASouoPt8cQFkwSBb1kU65ZCX2qzAvgBksrBgE7HtByO827oEBgXUbJ1BET2N5rTfosQ1Hhkk= valleedelisle@redhat.valleedelisle.nat
```

- The `resources/deploy.sh` will add a systemd unit for the notifierd and install all python modules necessary. This is the script called by the Gitlab's CI

## TODO
- Complete automatic reporting of events twice per day
- Bugzilla integration and reporting

## Author
David Vallee Delisle <dvd@redhat.com>

[![pipeline status](https://gitlab.cee.redhat.com/dvalleed/hydra-notifierd/badges/master/pipeline.svg)](https://gitlab.cee.redhat.com/dvalleed/hydra-notifierd/commits/master)

# Table of Contents
1. [Description](#description)
2. [Events](#events)
3. [Installation](#installation)
4. [Author](#author)

## Description
This notifier should be executed every X minutes. Every execution downloads the list of cases from the [Hydra API](https://mojo.redhat.com/groups/cee-integration/blog/2016/12/06/hydra-rest-api). If a case matches the criterias specified, it will trigger a notification. Here's the list of the current notification type supported:
- SMS (using [Twilio](https://www.twilio.com/))
- Mail (using [Mailgun](https://www.mailgun.com/)) or using a standard SMTP
- Logfile

## Events
This is the list of events that will trigger a notification:
- Severity change
- RME is activated
- Case is escalated
- Critical Situation is activated
- Customer Escalation
- FTS (24x7) is activated
- SBT is breached, or nearly breached, it's customizable
- New case in Queue

It's quite easy to add more, or tweak the current ones. Let me know if we need to change something.

All other events are still logged in the database for reporting and analysis.

## Installation

- Clone this repository

```
$ git clone git@gitlab.cee.redhat.com:dvalleed/hydra-notifierd.git
```

- To send email notification, you need to have a [Mailgun](https://www.mailgun.com/) account. It's free.

- To send SMS notification, you need to have a [Twilio](https://www.twilio.com) account. It's very cheap.

- Build a venv

```
$ virtualenv-3 .venv
```

- Install requirements

```
$ pip3 install -r requirements.txt
```

- Edit `hydra-notifierd.conf`

- You can add the secrets and password un `hydra-notifierd-secrets.conf`

- Execute the `hydra-notifierd.py` script after loading the venv

```
$ source .venv/bin/activate
$ ./hydra-notifierd.py
```

- Add a key to `authorized_keys` for automated deploy
```
command="/git/hydra-notifier/resources/deploy.sh",no-port-forwarding,no-x11-forwarding,no-agent-forwarding ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBEknEO6tjWf7rX7ASouoPt8cQFkwSBb1kU65ZCX2qzAvgBksrBgE7HtByO827oEBgXUbJ1BET2N5rTfosQ1Hhkk= valleedelisle@redhat.valleedelisle.nat
```

## TODO
- Automatic reporting of events twice per day
- Bugzilla integration


## Author
David Vallee Delisle <dvd@redhat.com>

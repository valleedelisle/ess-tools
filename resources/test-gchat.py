#!/usr/bin/env python3.6
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from lib.gchat import Gchat
from lib.log import Log
scopes = 'https://www.googleapis.com/auth/chat.bot'
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'service-account.json', scopes)
chat = build('chat', 'v1', http=credentials.authorize(Http()), cache_discovery=False)


case_data = {
             'caseNumber': '1234',
             'account': 'test',
             'accountNumber': '123',
             'caseOwner': 'dvd',
             'caseContact': 'Someone',
             'subject': 'Test case',
             'fts': True,
             'text': "test",
             'sfdc_url': "http://google.ca",
             'ascension_url': "http://google.com",
             'sbt': '10',
             'requestManagementEscalation': True,
             'lastUpdateDate': datetime.datetime.now(),
             'lastModifiedDate': datetime.datetime.now(),
             'createdDate': datetime.datetime.now(),
             'internalStatus': 'Waiting on nothing',
             'status': 'Waiting on IBM',
             'sbrGroup': 'Stack',
             'remoteSessionCount': 10,
             'version': 1,
             'numberOfBreaches': 0,
             'isEscalated': True,
             'critSit': True,
             'customerEscalation': True,
             'severity': 1
}
log = Log(debug = True, log_file = "test-gchat.log")
gchat = Gchat(case_data)
room_name = 'spaces/AAAAXvmO3fA'
resp = chat.spaces().messages().create(
  parent=room_name,
  body=gchat.getCard()).execute()
log.info("Gchat response: %s" % (resp))

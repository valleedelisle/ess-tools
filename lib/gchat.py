"""
Google chat object that is being sent to the gchat api
"""

class Gchat():
  # pylint: disable=too-few-public-methods
  # I'm not gonna create methods for fun
  """
  This is the class for gchat object
  """
  def __init__(self, event, should_update=None):
    self.event = event
    self.case = event.case
    self.card = {
      'actionResponse': {
        'type': 'UPDATE_MESSAGE' if should_update else 'NEW_MESSAGE'
      },
      'cards': [{
        'header': {
          'subtitle': "%s".format(self.event.text),
          'title': "{caseNumber} - {severity}".format(**self.event.case_data)
        },
        'sections': [{
          'widgets': [
            {'buttons': [
              {'textButton': {
                'text': 'SFDC',
                'onClick': {
                  'openLink': {
                    'url': "{sfdc_url}".format(**self.event.case_data),
                  }
                }
              }},
              {'textButton': {
                'text': 'Ascension',
                'onClick': {
                  'openLink': {
                    'url': "{ascension_url}".format(**self.event.case_data),
                  }
                }
              }},
              {'textButton': {
                'text': 'Customer-Portal',
                'onClick': {
                  'openLink': {
                    'url': "{customer_portal_url}".format(**self.event.case_data),
                  }
                }
              }}
            ]}
          ]
        }]
      }]
    }
    self.add_key("FTS", "{fts}")
    self.add_key("RME", "{requestManagementEscalation}")
    self.add_key("SBT", "{sbt}")
    self.add_key("SBR", "{sbrGroup}")
    self.add_key("Created", "{createdDate}")
    self.add_key("Updated", "{lastUpdateDate}")
    self.add_key("Owner", "{case_owner}")
    self.add_key("{account[name]}  ({accountNumber})", "{subject}",
                 "Contact: {caseContact}", "true")

  def add_key(self, top_label, content, bottom_label=None, multiline=False):
    """
    Function that adds a key/value to the card
    """
    kdict = {
      "content": content.format(**self.event.case_data),
      "topLabel": top_label.format(**self.event.case_data),
      "contentMultiline": multiline,
    }

    if bottom_label:
      kdict["bottomLabel"] = bottom_label.format(**self.event.case_data)

    self.card['cards'][0]['sections'][0]['widgets'].insert(0, {'keyValue': kdict})

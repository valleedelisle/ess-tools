# pylint: disable=no-member
"""
Creates a container to spawn a mariadb pod.
This container will call the oc_mariapod.py script
"""

import logging
import re
import time
from kubernetes import client
from lib.shift.podbase import PodBase
from lib.shift.resources import Pod, App

LOG = logging.getLogger("make_mariapod")

class MakeMariapod(PodBase):
  """
  MakeMariaDB Pod Class
  """
  service_port = None
  service_protocol = None
  service_name = None
  storage_size = None
  storage_access_mode = None
  app_label = 'make-mariadb'
  image = 'docker-registry.default.svc:5000/ess/ess-tools:latest'
  name = 'make_mariadb'
  namespace = 'ess'
  cluster = 'https://paas.psi.redhat.com:443'
  token = None
  debug = False
  args = None
  resource_req = client.V1ResourceRequirements(
    limits={"cpu": 1, "memory": "1Gi"},
    requests={"cpu": 1, "memory": "1Gi"}
  )
  def __init__(self, **kwargs):
    """
    We pull the class attributes and store them in the instance
    """
    super(MakeMariapod, self).__init__()
    for key in dir(self.__class__):
      if (not key.startswith('_') and
          not callable(getattr(self.__class__, key))):
        setattr(self, key, getattr(self.__class__, key))
    # Let's also store the arguments parsed
    self.__dict__.update(kwargs)
    LOG.info("Generating resources")
    self.generate()
    if self.deploy:
      LOG.info("Deploying the resources")
      self.create()
    if self.delete_deploy:
      LOG.info("Deleting resources for name %s", self.name)
      self.pod.delete()
      self.app.delete()
    else:
      LOG.info("Listing resources for name %s", self.name)
      self.pod.show()
      self.app.show()

  def generate(self):
    """
    Generate the Resource objects
    """
    self.pod = Pod(self)
    self.app = App(self)

  def create(self):
    """
    Sends the objects to the OSC API
    """
    self.app.post()

  def check(self):
    """
    Returns when everyone is ready,
    or after max_validation_retries
    """
    self.pod.check()
    self.app.check()

  def env(self):
    """
    Container customisation with environment variables
    """
    command = " ".join(self.command)
    #return [client.V1EnvVar(name='APP_SCRIPT', value='./oc_mariadb.py ' + command)]
    return [client.V1EnvVar(name='APP_SCRIPT', value='find .')]

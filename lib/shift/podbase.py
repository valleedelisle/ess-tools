"""
PodBase object
"""

from kubernetes import client

from lib.base import Base

class PodBase(Base):
  from kubernetes import client
  """
  Pod Base Class
  """
  service_port = None
  service_protocol = None
  service_name = None
  storage_size = None
  storage_access_mode = None
  volume_suffix = None
  app_label = 'generic-app'
  image = None
  name = None
  namespace = 'ess'
  cluster = 'https://paas.psi.redhat.com:443'
  token = None
  debug = False
  volumes = []
  resource_req = client.V1ResourceRequirements(
    limits={"cpu": 1, "memory": "1Gi"},
    requests={"cpu": 1, "memory": "1Gi"}
  )
  args = []
  def __init__(self, **kwargs):
    """
    We pull the class attributes and store them in the instance
    """
    for key in dir(self.__class__):
      if (not key.startswith('_') and
          not callable(getattr(self.__class__, key))):
        setattr(self, key, getattr(self.__class__, key))
    # Let's also store the arguments parsed
    self.__dict__.update(kwargs)

  def init_containers(self):
    """
    Returns a curl container object that will download the case attachment
    """
    return None

  def check(self):
    """
    Returns when everyone is ready,
    or after max_validation_retries
    """
    return None

  def env(self):
    """
    Container customisation with environment variables
    """
    return None

  def mounts(self):
    """
    Returns the mounts object
    based on volumes class variable
    """
    return None

  def volume_list(self):
    """
    Returns the volumes resource obj
    """
    return None

  def ports(self):
    """
    Returns list of exposed port(s)
    """
    return None

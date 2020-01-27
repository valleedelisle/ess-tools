import logging
import time
import traceback
from kubernetes import client
from lib.mysql_connector import MysqlConnect
from lib.base import Base
from lib.shift.resources import Pvc, Pv, Svc, Pod, App

LOG = logging.getLogger("mariapod")

class Mariapod(Base):
  service_port = 3306
  service_protocol = 'TCP'
  service_name = 'mariadb'
  storage_size = '20Gi'
  storage_access_mode = 'ReadWriteMany'
  volume_suffix = 'data'
  app_label = 'cu-dump'
  image = 'mariadb:latest'
  name = 'mariadb'
  namespace = 'ess'
  cluster = 'https://paas.psi.redhat.com:443'
  token = None
  debug = False

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
    self.generate()
    if self.deploy:
      self.create()
      self.check()
    elif self.delete_deploy:
    #  self.pv.delete()
      self.pvc.delete()
      self.svc.delete()
      self.pod.delete()
      self.app.delete()
    else:
      LOG.info("Listing resources for name %s" % self.name)
      self.pvc.show()
      self.svc.show()
      self.pod.show()
      self.app.show()

  def generate(self):
    self.pvc = Pvc(self)
    self.pv = Pv(self)
    self.svc = Svc(self)
    self.pod = Pod(self)
    self.app = App(self)

  def create(self):
    self.pvc.post()
    self.svc.post()
    self.app.post()

  def check(self):
    self.pvc.check()
    self.pod.check()
    self.app.check()
    self.svc.check()

  def load_db(self):
    self.mysql = MysqlConnect()
    try:
      with open(self.dump_file) as f:
          cursor.execute(f.read().decode('utf-8'), multi=True)
    except Exception as error: # pylint: disable=broad-except
      LOG.error("load_db() failed on %: %s" % (self.dump_file, error))
      LOG.error("%s" % traceback.format_exc())
      raise Exception('ImportError', 'Unable to import mysql file')


  def env(self):
    """
    Container customisation with environment variables
    """
    return [client.V1EnvVar(name='MYSQL_USER', value='ess-automation'),
            client.V1EnvVar(name='MYSQL_PASSWORD', value='q1w2e3'),
            client.V1EnvVar(name='MYSQL_ROOT_PASSWORD', value='q1w2e3')]

  def mounts(self):
    return [client.V1VolumeMount(mount_path='/var/lib/mysql',
                                 name=self.name+'-' + self.volume_suffix,
                                 sub_path='mysql')]

  def ports(self):
    return [client.V1ContainerPort(container_port=self.service_port)]

  def __setattr__(self, key, value):
    super().__setattr__(key, value)
 

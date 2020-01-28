import logging
import re
import time
import traceback
import os
import sys
import codecs
import base64
from chardet.universaldetector import UniversalDetector
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
  mysql_user = 'ess-automation'
  mysql_password = 'q1w2e3'
  mysql_root_password = 'q1w2e3'
  dump_file = None
  mysql = None
  data_format = 'utf-8'
  volumes = [{ 'mount_path': '/var/lib/mysql',
               'name': 'data',
               'sub_path': 'mysql'},
             { 'mount_path': '/docker-entrypoint-initdb.d',
               'name': 'init',
               'sub_path': 'docker-entrypoint-initdb.d'}]
  resource_req = client.V1ResourceRequirements(                                                                                                                                                                                                                                                                                                                                                                                           
    limits={"cpu": 1, "memory": "1Gi"},
    requests={"cpu": 1, "memory": "1Gi"}
  )
  args = (
    '--max_allowed_packet=128M',
    '--character-set-server=utf8'
  )
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
    LOG.info("Generating resources")
    self.generate()
    if self.deploy:
      LOG.info("Deploying the resources")
      self.create()
      LOG.info("Validating status")
      self.check()
    if self.delete_deploy:
      LOG.info("Deleting resources for name %s" % self.name)
      for vol in self.volumes:
        getattr(self, 'pvc_' + vol['name']).delete()
      self.svc.delete()
      self.pod.delete()
      self.app.delete()
    else:
      LOG.info("Listing resources for name %s" % self.name)
      for vol in self.volumes:
        getattr(self, 'pvc_' + vol['name']).show()
      self.svc.show()
      self.pod.show()
      self.app.show()
      LOG.info("mysql -u root --password=%s -h %s -P %s" % (self.mysql_root_password, self.pod.host_ip, self.svc.node_port))

  def generate(self):
    for vol in self.volumes:
      setattr(self, 'pvc_' + vol['name'], Pvc(self, suffix=vol['name']))
      setattr(self, 'pv_' + vol['name'], Pv(self, suffix=vol['name']))
    self.svc = Svc(self)
    self.pod = Pod(self)
    self.app = App(self)

  def init_container(self):
    return client.V1Container(name=self.name + '-init',
                                image='appropriate/curl',
                                args=[
                                  '-u', self.username + ':' + self.password,
                                  '-o', '/docker-entrypoint-initdb.d/init.sql',
                                  '$(URL)',
                                ],
                                volume_mounts=self.mounts(),
                                resources=self.resource_req,
                                env=[client.V1EnvVar(name='URL', value=self.dump_file)],
                             )
  def create(self):
    for vol in self.volumes:
      getattr(self, 'pvc_' + vol['name']).post()
    self.svc.post()
    self.app.post()

  def check(self):
    for vol in self.volumes:
      getattr(self, 'pvc_' + vol['name']).check()
    self.pod.check()
    self.app.check()
    self.svc.check()

  def env(self):
    """
    Container customisation with environment variables
    """
    return [client.V1EnvVar(name='MYSQL_USER', value=self.mysql_user),
            client.V1EnvVar(name='MYSQL_PASSWORD', value=self.mysql_password),
            client.V1EnvVar(name='MYSQL_ROOT_PASSWORD', value=self.mysql_root_password)]

  def mounts(self):
    return [client.V1VolumeMount(mount_path=vol['mount_path'],
                                 name=self.name + '-' + vol['name'],
                                 sub_path=vol['sub_path'])
            for vol in self.volumes]

  def volume_list(self):
      return [getattr(self, 'pv_' + vol['name']).resource for vol in self.volumes]


  def ports(self):
    return [client.V1ContainerPort(container_port=self.service_port)]

  def __setattr__(self, key, value):
    super().__setattr__(key, value)
 

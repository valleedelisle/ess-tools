from kubernetes import client
import logging
from lib.pod import Pod

LOG = logging.getLogger("root.mariapod")

class Mariapod(Pod):
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
    self.__dict__.update(kwargs)
    super(Mariapod, self).__init__()

  def create(self):
    self.post_pvc()
    self.post_svc()
    self.post_app()

  def env(self):
    return [client.V1EnvVar(name='MYSQL_USER', value='ess-automation'),
            client.V1EnvVar(name='MYSQL_PASSWORD', value='q1w2e3'),
            client.V1EnvVar(name='MYSQL_ROOT_PASSWORD', value='q1w2e3')]

  def mounts(self):
    return [client.V1VolumeMount(mount_path='/var/lib/mysql',
                                 name=self.name+'-' + self.volume_suffix,
                                 sub_path='mysql')]

  def ports(self):
    return [client.V1ContainerPort(container_port=self.service_port)]

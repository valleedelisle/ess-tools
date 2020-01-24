import logging
from kubernetes import client
from lib.base import Base

LOG = logging.getLogger('root.shift.resource')

class ResourceBase(Base):
  long_name = None
  short_name = None
  api = None
  resource = None
  items = None
  connection_debug = False
  api_list = {'core': 'CoreV1Api', 'apps': 'AppsV1Api'}

  def __init__(self):
    for key in sorted(self.obj.__dict__.keys()):
      if not key.startswith('_'):
        print("Base", key, getattr(self.obj, key) )
        setattr(self, key, getattr(self.obj, key))
    configuration = client.Configuration()
    configuration.host = self.cluster
    configuration.api_key['authorization'] = self.token
    configuration.api_key_prefix['authorization'] = 'Bearer'
    configuration.verify_ssl=False
    configuration.debug = self.connection_debug
    self.api_connection = getattr(client, self.api_list[self.api])(client.ApiClient(configuration))

  def label(self):
    return {'app': self.app_label + '-' + self.name}
 
  def metadata(self, object_name):
    """
    returns metadata object
    """
    return client.V1ObjectMeta(name=object_name + '-' + self.name,
                               labels=self.label())

  def selector(self):
    """
    returns selector dict
    """
    return {'matchLabels': self.label() }

  def get(self):
    func = getattr(self.api_connection, 'list_namespaced_' + self.long_name)
    print("Function %s NAmespace: %s" % (func, self.namespace))
    try:
      self.items = func(self.namespace)
    except client.rest.ApiException as exc:
      LOG.debug("API returned an error for resource %s: %s" % (self.short_name, exc))
      pass
    LOG.debug('%s list: %s' % (self.short_name, self.items))

  def post(self):
    func = getattr(self.api_connection, 'create_namespaced_' + self.long_name)
    gen_obj = getattr(self.obj, self.short_name).resource
    LOG.debug('%s Deployment %s' % (self.short_name, self.resource))
    self.resp = func(body=gen_obj, namespace=self.namespace)
    LOG.debug('%s Deployment created. status="%s"' % (self.short_name, str(self.resp.status)))

  def check(self):
    if self.items:
      for item in self.items.items:
        print(item.status)
    else:
      LOG.debug("No objects for resource %s" % self.short_name)

class Pvc(ResourceBase):
  long_name = 'persistent_volume_claim'
  short_name = 'pvc'
  api = 'core'
  def __init__(self, obj):
    self.obj = obj
    super(Pvc, self).__init__()
    volume_name = self.name + '-' + self.volume_suffix
    requirements = client.V1ResourceRequirements(requests={
                                                   'storage': self.storage_size
                                                 })
    spec = client.V1PersistentVolumeClaimSpec(access_modes=[self.storage_access_mode],
                                                   resources=requirements,
                                                   selector=self.selector())
    self.resource = client.V1PersistentVolumeClaim(metadata=self.metadata('claim'), spec=spec)

class Pv(ResourceBase):
  long_name = 'persistent_volume'
  short_name = 'pv'
  api = 'core'
  def __init__(self, obj):
    self.obj = obj
    super(Pv, self).__init__()
    claim_name = 'claim-' + self.name
    claim = client.V1PersistentVolumeClaimVolumeSource(claim_name=claim_name)
    self.resource = client.V1Volume(name=self.name + '-' + self.volume_suffix,
                                    persistent_volume_claim=claim)
class Svc(ResourceBase):
  long_name = 'service'
  short_name = 'svc'
  api = 'core'
  def __init__(self, obj):
    self.obj = obj
    super(Svc, self).__init__()
    svc_port = client.V1ServicePort(name=self.service_name,
                                    port=self.service_port,
                                    protocol=self.service_protocol)
    spec = client.V1ServiceSpec(
        ports=[svc_port],
        type='NodePort',
    )
    self.resource = client.V1Service(
                      api_version='v1',
                      kind='Service',
                      metadata=self.metadata('svc'),
                      spec=spec
    )

class Pod(ResourceBase):
  long_name = 'pod'
  short_name = 'pod'
  api = 'core'
  def __init__(self, obj):
    self.obj = obj
    super(Pod, self).__init__()
    self.resource = client.V1Container(name=self.name,
                                       image=self.image,
                                       env=obj.env(),
                                       volume_mounts=obj.mounts(),
                                       ports=obj.ports())

class App(ResourceBase):
  long_name = 'deployment'
  short_name = 'app'
  api = 'apps'
  def __init__(self, obj):
    self.obj = obj
    super(App, self).__init__()
    pod_spec = client.V1PodSpec(containers=[obj.pod.resource],
                                volumes=[obj.pv.resource])
    print("DVD PODSPEC", pod_spec)

    template = client.V1PodTemplateSpec(
                 metadata=self.metadata('pod-template'),
                 spec=pod_spec)
    spec = client.V1DeploymentSpec(
             replicas=1,
             template=template,
             selector=self.selector())

    self.resource = client.V1Deployment(
        api_version='apps/v1',
        kind='Deployment',
        metadata=self.metadata(self.app_label),
        spec=spec
    )

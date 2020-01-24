import logging
from time import sleep
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
  good_status = None
  max_validation_retry = 30
  api_list = {'core': 'CoreV1Api', 'apps': 'AppsV1Api'}

  def __init__(self):
    for key in sorted(self.obj.__dict__.keys()):
      if not key.startswith('_'):
        setattr(self, key, getattr(self.obj, key))
    configuration = client.Configuration()
    configuration.host = self.cluster
    configuration.api_key['authorization'] = self.token
    configuration.api_key_prefix['authorization'] = 'Bearer'
    configuration.verify_ssl=False
    configuration.debug = self.connection_debug
    self.api_connection = getattr(client, self.api_list[self.api])(client.ApiClient(configuration))

  def label_dict(self):
    """
    returns label dictionnary used for resource creation
    """
    return {'app': self.app_label + '-' + self.name}

  def label(self):
    """
    returns label k=v used when listing resources
    """
    label_key = next(iter(self.label_dict()))
    label_value = self.label_dict()[label_key]
    return "{}={}".format(label_key, label_value)

  def metadata(self, object_name):
    """
    returns metadata object
    """
    return client.V1ObjectMeta(name=object_name + '-' + self.name,
                               labels=self.label_dict())

  def selector(self):
    """
    returns selector dict
    """
    return {'matchLabels': self.label_dict() }

  def get_all(self):
    """
    list all resources of a kind and stores in self.items
    """
    func = getattr(self.api_connection, 'list_namespaced_' + self.long_name)
    try:
      self.items = func(self.namespace, label_selector=self.label())
    except client.rest.ApiException as exc:
      LOG.info("API returned an error for resource %s: %s" % (self.short_name, exc))
      pass
    LOG.debug('%s get_all: %s' % (self.short_name, self.items))

  def get(self, name):
    func = getattr(self.api_connection, 'read_namespaced_' + self.long_name)
    try:
      self.item = func(namespace=self.namespace, name=name)
      LOG.debug("Refreshing %s %s: %s" % (self.short_name, name, self.item))
    except client.rest.ApiException as exc:
      LOG.info("API returned an error for resource %s %s: %s" % (self.short_name, name, exc))
      pass
    LOG.debug('%s get %s: %s' % (self.short_name, name, self.item))
    return self.item

  def post(self):
    func = getattr(self.api_connection, 'create_namespaced_' + self.long_name)
    gen_obj = getattr(self.obj, self.short_name).resource
    LOG.debug('%s Deployment %s' % (self.short_name, self.resource))
    self.resp = func(body=gen_obj, namespace=self.namespace)
    LOG.debug('%s Deployment created. status="%s"' % (self.short_name, str(self.resp.status)))

  def validate(self):
    if not self.good_status:
      return True
    if self.items:
      for item in self.items.items:
        if item.status.phase != self.good_status:
          return False
      return True


  def check(self):
    if not self.items:
      LOG.debug("No objects for resource %s, running get_all()" % self.short_name)
      self.get_all()
    if self.items:
      LOG.debug("Validating Type %s" % (self.short_name))
      validate = False
      validation_retries = 0
      while validate is False:
        validation_retrie += 1
        if validation_retries >= self.max_validation_retry:
          LOG.debug("Object %s" % (self.items))
          LOG.error("Failed to validate %s" % (self.short_name))
          raise Exception('ValidationError', 'Unable to validate the creation of resource on Shift')
        validate = self.validate()
        LOG.debug("validate() returns %s" % (validate))
        if not validate:
          LOG.debug("No validation")
        for item in self.items.items:
          self.get_all()
          LOG.debug("Type %s Item %s Status: %s" % (self.short_name, item.metadata.name, item.status))
        sleep(2)
    else:
      LOG.error("No items returned by list_namespaced")
  
class Pvc(ResourceBase):
  long_name = 'persistent_volume_claim'
  short_name = 'pvc'
  good_status = "Bound"
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
  good_status = "Running"
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
  def validate(self):
    if self.items:
      for item in self.items.items:
        if item.status.replicas != item.status.ready_replicas:
          return False
      return True

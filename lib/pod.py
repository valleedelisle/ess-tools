"""
Pod Object
"""
from kubernetes import client
import logging

LOG = logging.getLogger("root.pod")

class Pod(object):
  # List of objects
  resource_list = {
    'pvc': { 'long': 'persistent_volume_claim', 'api': 'core' },
    'pv': {'long': 'persistent_volume', 'api': 'core' },
    'svc': {'long': 'service', 'api': 'core' },
    'pod': {'long': 'pod', 'api': 'core' },
    'pod_template': {'long': 'pod_template', 'api': 'core' },
    'app': {'long': 'deployment', 'api': 'apps' },
  }

  def __init__(self):
    configuration = client.Configuration()
    configuration.host = self.cluster
    configuration.api_key['authorization'] = self.token
    configuration.api_key_prefix['authorization'] = 'Bearer'
    configuration.verify_ssl=False
    configuration.debug = self.debug
    self.core_api = client.CoreV1Api(client.ApiClient(configuration))
    self.apps_api = client.AppsV1Api(client.ApiClient(configuration))
    for res in self.resource_list:
      setattr(self, 'list_' + res, None)
      self.make_methods(res)

  def make_methods(self, res):
    api = getattr(self, self.resource_list[res]['api'] + '_api')
    def return_k8s_function(name):
      func_get = getattr(api, name + self.resource_list[res]['long'])
    def get(self):
      func_get = return_k8s_function('list_namedspaced_')
      setattr(self, "list_" + res, func_get(self.namespace))
      LOG.debug('%s list: %s' % (res, getattr(self, 'list_' + res)))
    setattr(self, 'get_' + res, get) 

    def post(self):                  
      gen_obj = getattr(self, res)
      func_post = return_k8s_function('create_namedspaced_')
      LOG.debug('%s Deployment %s' % gen_object)
      self.resp = func_post(body=gen_obj, namespace=self.namespace)
      LOG.debug('%s Deployment created. status="%s"' % (res, str(self.resp.status)))
    setattr(self, 'post_' + res, post) 

    def check(self):
      list_obj = getattr(self, 'list_' + res)
      for item in list_obj.items:
        print(item.status.succeded)
    setattr(self, 'check_' + res, check) 

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

  def pvc(self):
    """
    returns PersistentVolumeClaim object
    """
    volume_name = self.name + '-' + self.volume_suffix
    requirements = client.V1ResourceRequirements(requests={
                                                   'storage': self.storage_size
                                                 })
    spec = client.V1PersistentVolumeClaimSpec(access_modes=[self.storage_access_mode],
                                                   resources=requirements,
                                                   selector=self.selector())
    return client.V1PersistentVolumeClaim(metadata=self.metadata('claim'), spec=spec)

  def vol(self):
    """
    returns volume object based on PVC
    """
    claim_name = 'claim-' + self.name
    claim = client.V1PersistentVolumeClaimVolumeSource(claim_name=claim_name)
    return client.V1Volume(name=self.name + '-' + self.volume_suffix,
                           persistent_volume_claim=claim)

  def svc(self):
    """
    returns a service with NodePort
    """
    metadata = self.metadata('svc')
    svc_port = client.V1ServicePort(name=self.service_name,
                                    port=self.service_port,
                                    protocol=self.service_protocol)
    spec = client.V1ServiceSpec(
        ports=[svc_port],
        type='NodePort',
    )
    return client.V1Service(
        api_version='v1',
        kind='Service',
        metadata=metadata,
        spec=spec
    )

  def container(self):
    return client.V1Container(name=self.name,
                              image=self.image,
                              env=self.env(),
                              volume_mounts=self.mounts(),
                              ports=self.ports())

  def pod_spec(self):
    return client.V1PodSpec(containers=[self.container()],
                            volumes=[self.vol()])
 
  def pod(self):
    template = client.V1PodTemplateSpec(
                 metadata=self.metadata('pod-template'),
                 spec=self.pod_spec())
    spec = client.V1DeploymentSpec(
             replicas=1,
             template=template,
             selector=self.selector())

    return client.V1Deployment(
        api_version='apps/v1',
        kind='Deployment',
        metadata=self.metadata(self.app_label),
        spec=spec
    )
  
  def __repr__(self):
    return '%s(%s)' % (
      (self.__class__.__name__),
      ', '.join(['%s=%r' % (key, getattr(self, key))
                 for key in sorted(self.__dict__.keys())
                 if not key.startswith('_')]))

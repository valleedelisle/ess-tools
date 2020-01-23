"""
Pod Object
"""
from kubernetes import client
import logging

LOG = logging.getLogger("root.pod")

class Pod(object):
  def __init__(self):
    configuration = client.Configuration()
    configuration.host = self.cluster
    configuration.api_key['authorization'] = self.token
    configuration.api_key_prefix['authorization'] = 'Bearer'
    configuration.verify_ssl=False
    configuration.debug = self.debug
    self.core_api = client.CoreV1Api(client.ApiClient(configuration))
    self.apps_api = client.AppsV1Api(client.ApiClient(configuration))

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

  def node_service(self):
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
  
  def post_pvc(self):
    pvc = self.pvc()
    LOG.debug('PVC Deployment %s' % pvc)
    self.resp = self.core_api.create_namespaced_persistent_volume_claim(
        body=pvc,
        namespace=self.namespace)
    LOG.debug('PVC Deployment created. status="%s"' % str(self.resp.status))

  def post_svc(self):
    svc = self.node_service()
    LOG.debug('SVC Deployment %s' % svc)
    self.resp = self.core_api.create_namespaced_service(
        body=svc,
        namespace=self.namespace)
    LOG.debug('SVC Deployment created. status="%s"' % str(self.resp.status))

  def post_app(self):
    app = self.pod()
    LOG.debug('App Deployment %s' % app)
    self.resp = self.apps_api.create_namespaced_deployment(
        body=app,
        namespace=self.namespace)
    LOG.debug('App Deployment created. status="%s"' % str(self.resp))

  def __repr__(self):
    return '%s(%s)' % (
      (self.__class__.__name__),
      ', '.join(['%s=%r' % (key, getattr(self, key))
                 for key in sorted(self.__dict__.keys())
                 if not key.startswith('_')]))

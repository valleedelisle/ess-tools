#!/usr/bin/env python3
from os import path

import yaml

from kubernetes import client, config, utils
import argparse
 
def parse_args():
  """
  Function to parse arguments
  """
  parser = argparse.ArgumentParser(description='source database into container')
  parser.add_argument('--debug',
                      action='store_true',
                      default=False,
                      help='Display debug information')
  parser.add_argument('--progress',
                      action='store_true',
                      dest='show_progress',
                      default=False,
                      help='Show progressbar during parsing')
  parser.add_argument('-t', '--token',
                      action='store',
                      default='eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJlc3MiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlY3JldC5uYW1lIjoiZXNzLWF1dG9tYXRpb24tdG9rZW4tYzJjdmMiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZXNzLWF1dG9tYXRpb24iLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiJjYWVkMjMxZC0zY2E0LTExZWEtOWUyZi1mYTE2M2VjMjI5YzAiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6ZXNzOmVzcy1hdXRvbWF0aW9uIn0.uf651FKxjnPbHsZoa1-l1JLhXF6BHKn9hoGYuSVWzj-m8uwFQAQsoNDP2opwq69c-7WbiPnZL9ByvaiMOyzIuEGCW_0n5W1jjPHneUn-lpBUpTQPMtTbn5RK15hDZ_5WjVmGPFfcMxio0EcVbWNj3ZL_pXoGyuvxYJSfJ0IU9-Nbz0cEnCi6Avms2mOj35ZZgIQBbGu2XELfoIoxAcn92j7tV6b5zRq9Ph4E3tNw_Jb1zOySyGkFa1ySfoFp9BP4xs5bWryhr2pDiMrrkdrYem4QJPCmPbV-8aSHsgc0XyossbmLEkGw8e5WWsgrOmbMwLNhf93DQNfNm7Zh_QNIWg',
                      type=str,
                      help='Token used for authentication')
  parser.add_argument('-n', '--name',
                      action='store',
                      required=True,
                      type=str,
                      help='Name for the container, normally this is the case number')
  parser.add_argument('--cluster',
                      action='store',
                      default='https://paas.psi.redhat.com',
                      type=str,
                      help='OpenShift Cluster address')
 
  parser.add_argument('--namespace',
                      action='store',
                      default='ess',
                      type=str,
                      help='Namespace or openshift project')
  parser.add_argument('--dump-file', type=str, action='store')
 
  return parser.parse_args()

class Shiftdeployment(object):
  def __init__(self, **kwargs):
    self.__dict__.update(kwargs)
    self.client = client
    self.configuration = self.client.Configuration()
    self.configuration.host = self.cluster
    self.configuration.api_key['authorization'] = self.token
    self.configuration.api_key_prefix['authorization'] = 'Bearer'
    self.configuration.verify_ssl=False
    self.configuration.debug = self.debug
    self.core_api = self.client.CoreV1Api(self.client.ApiClient(self.configuration))
    self.apps_api = self.client.AppsV1Api(self.client.ApiClient(self.configuration))
    self.__dict__.update(kwargs)
    pvc = self.create_pvc()
    print('Creating pvc %s' % pvc)
    self.post_pvc(pvc)
    svc = self.create_service(3306)
    print('Creating svc %s' % svc)
    self.post_svc(svc)
    pod = self.create_pod()
    print('Creating pod %s' % pod)
    self.app_deployment(pod)

  def get_metadata(self, object_name):
    return self.client.V1ObjectMeta(name=object_name + '-' + self.name, labels={'app': 'cu-dump-' + self.name})

  def get_selector(self):
    return {'matchLabels': {'app': 'cu-dump-' + self.name}}

  def create_pvc(self, access_mode='ReadWriteMany', storage='50Gi', volume_suffix='data'):
    volume_name = self.name + '-' + volume_suffix
    requirements = self.client.V1ResourceRequirements(requests={'storage': '50Gi'})
    spec = self.client.V1PersistentVolumeClaimSpec(access_modes=[access_mode],
                                                   resources=requirements,
                                                   selector=self.get_selector())
    return self.client.V1PersistentVolumeClaim(metadata=self.get_metadata('claim'), spec=spec)

  def create_vol(self):
    claim_name = 'claim-' + self.name
    claim = self.client.V1PersistentVolumeClaimVolumeSource(claim_name=claim_name)
    return self.client.V1Volume(name=self.name + '-data', persistent_volume_claim=claim)

  def create_container(self, image='mariadb:latest'):
    envvar = [self.client.V1EnvVar(name='MYSQL_USER', value='ess-automation'),
              self.client.V1EnvVar(name='MYSQL_PASSWORD', value='q1w2e3'),
              self.client.V1EnvVar(name='MYSQL_ROOT_PASSWORD', value='q1w2e3')]
    mounts = [self.client.V1VolumeMount(mount_path='/var/lib/mysql', name=self.name+'-data', sub_path='mysql')]
    return self.client.V1Container(name=self.name,
                                   image=image,
                                   env=envvar,
                                   volume_mounts=mounts,
                                   ports=[self.client.V1ContainerPort(container_port=3306)])

  def create_pod(self):
    # Configureate Pod template container
    container = self.create_container()
    volume = self.create_vol()
    spec=self.client.V1PodSpec(containers=[container], volumes=[volume])
    # Create and configurate a spec section
    template = self.client.V1PodTemplateSpec(
        metadata=self.get_metadata('pod-template'),
        spec=spec)
    # Create the specification of deployment
    spec = self.client.V1DeploymentSpec(
        replicas=1,
        template=template,
        selector=self.get_selector())
    # Instantiate the deployment object
    return self.client.V1Deployment(
        api_version='apps/v1',
        kind='Deployment',
        metadata=self.get_metadata('cu-dump'),
        spec=spec
    )
  
  def create_service(self, port):
    metadata = self.get_metadata('svc')
    svc_port = self.client.V1ServicePort(name='mysql', port=3306, protocol='TCP')
    spec = self.client.V1ServiceSpec(
        ports=[svc_port],
        type='NodePort',
    )
    return self.client.V1Service(
        api_version='v1', kind='Service', metadata=metadata, spec=spec
    )

  def post_pvc(self, deployment):
    print('PVC Deployment %s' % deployment)
    self.resp = self.core_api.create_namespaced_persistent_volume_claim(
        body=deployment,
        namespace=self.namespace)
    print('PVC Deployment created. status="%s"' % str(self.resp.status))

  def post_svc(self, deployment):
    # Create deployement
    print('SVC Deployment %s' % deployment)
    self.resp = self.core_api.create_namespaced_service(
        body=deployment,
        namespace=self.namespace)
    print('SVC Deployment created. status="%s"' % str(self.resp.status))

  def app_deployment(self, deployment):
    # Create deployement
    print('App Deployment %s' % deployment)
    self.resp = self.apps_api.create_namespaced_deployment(
        body=deployment,
        namespace=self.namespace)
    print('App Deployment created. status="%s"' % str(self.resp.status))

  def __repr__(self):
    return '%s(%s)' % (
      (self.__class__.__name__),
      ', '.join(['%s=%r' % (key, getattr(self, key))
                 for key in sorted(self.__dict__.keys())
                 if not key.startswith('_')]))

def main():
  args = parse_args()
  db_object = Shiftdeployment(**args.__dict__)
  print(db_object.resp)


if __name__ == '__main__':
    main()

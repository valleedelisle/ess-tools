# Introduction

- This container integrates python with the openshift-cli package.
- I was unable to find a docker image with openshift-cli and python3 so I made one.
- It's used for CI/CD in `.gitlab-ci.yml`
- It has to be built on a RHEL7 subscribed system because the base `openshift-cli` image is built on RHEL7

# Build instruction
```
$ docker login docker.io
$ docker build -t openshift-cli-python .
$ docker tag openshift-cli-python docker.io/valleedelisle/openshift-cli-python
$ docker push docker.io/valleedelisle/openshift-cli-python:latest
```

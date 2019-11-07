FROM openshift/origin-cli
MAINTAINER David Vallee Delisle <dvd@redhat.com>
ENV OC_VERSION=v3.11.0
RUN rm /etc/yum.repos.d/*.repo && yum-config-manager --enable rhel-7-server-htb-rpms --enable rhel-7-server-rpms && yum install -y python3 python3-libs python3-pip python3-setuptools git
CMD ["/usr/bin/oc"]

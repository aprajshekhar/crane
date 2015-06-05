# This runs crane (http://github.com/pulp/crane) on centos6
#
# Example usage:
# In the topmost directory of crane
# $ sudo docker build -t crane .
# $ docker run -p 80:80 -v ~/tests/data/metadata_good/:/var/lib/crane/metadata crane
# Test:
# curl -vu tom:redhat -X GET $DOCKER_IMAGE_IP/v1/_ping
# Search backends are not configured. Please do so in crane/data/default_config.conf before issuing docker build


FROM centos:centos7
MAINTAINER Pulp Team <pulp-list@redhat.com>

RUN yum -y install http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm

RUN yum update -y --nogpgcheck 

RUN yum install -y --nogpgcheck  python-flask python-pip httpd mod_wsgi python-rhsm

RUN mkdir -p /var/lib/crane/metadata/

ADD deployment/apache24_proxy.conf /etc/httpd/conf.d/crane.conf
ADD deployment/.htpasswd /etc/httpd/

ADD crane /usr/local/src/crane/crane
ADD setup.py /usr/local/src/crane/
ADD setup.cfg /usr/local/src/crane/
ADD requirements.txt /usr/local/src/crane/
ADD test-requirements.txt /usr/local/src/crane/
ADD run.py /usr/local/src/crane/
ADD LICENSE /usr/share/doc/python-crane/
ADD COPYRIGHT /usr/share/doc/python-crane/
ADD README.rst /usr/share/doc/python-crane/
ADD start.sh /start.sh
RUN pip install /usr/local/src/crane/

ENV APACHE_RUN_USER apache
ENV APACHE_RUN_GROUP apache

EXPOSE 80
CMD ["/bin/bash", "/start.sh"]

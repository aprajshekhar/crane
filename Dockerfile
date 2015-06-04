# This runs crane (http://github.com/pulp/crane) on centos6
#
# Example usage:
# $ sudo docker run -p 5000:80 -v /home/you/cranedata:/var/lib/crane/metadata pulp/crane

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
#ENTRYPOINT ["/usr/bin/python", "/usr/local/src/crane/run.py"]
CMD ["/bin/bash", "/start.sh"]
#CMD [/usr/local/src/crane/run.py]
#CMD ["/bin/bash"]
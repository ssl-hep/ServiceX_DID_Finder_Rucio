FROM rucio/rucio-clients:release-1.23.7.post1

LABEL maintainer Ilija Vukotic <ivukotic@cern.ch>

# Create app directory
WORKDIR /usr/src/app

# for CA certificates
USER root
RUN mkdir -p /etc/grid-security/certificates /etc/grid-security/vomsdir 

RUN yum -y update
RUN yum localinstall https://repo.opensciencegrid.org/osg/3.4/osg-3.4-el7-release-latest.rpm -y

RUN yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm; \
    curl -s -o /etc/pki/rpm-gpg/RPM-GPG-KEY-wlcg http://linuxsoft.cern.ch/wlcg/RPM-GPG-KEY-wlcg; \
    curl -s -o /etc/yum.repos.d/wlcg-centos7.repo http://linuxsoft.cern.ch/wlcg/wlcg-centos7.repo;

RUN yum install osg-ca-certs voms voms-clients wlcg-voms-atlas fetch-crl -y

# We need python3 which is not part of the Rucio docker image
RUN yum install -y centos-release-scl && \
     yum install -y rh-python36

# Okay, change our shell to specifically use our software collections.
# (default was SHELL [ "/bin/sh", "-c" ])
# https://docs.docker.com/engine/reference/builder/#shell
#
# See also `scl` man page for enabling multiple packages if desired:
# https://linux.die.net/man/1/scl
SHELL [ "/usr/bin/scl", "enable", "rh-python36" ]

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt


COPY scl_enable /usr/bin/scl_enable


COPY . .

# build  
RUN echo "Timestamp:" `date --utc` | tee /image-build-info.txt

ENV BASH_ENV="/usr/bin/scl_enable" \
    ENV="/usr/bin/scl_enable" \
    PROMPT_COMMAND=". /usr/bin/scl_enable"

ENV X509_USER_PROXY /etc/grid-security/x509up


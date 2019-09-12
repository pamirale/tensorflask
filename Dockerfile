#Download base image ubuntu 16.04
#FROM marketplace.gcr.io/google/ubuntu1604:latest
FROM gcr.io/gcp-runtimes/ubuntu_16_0_4:latest
LABEL "Maintainer"="ActiveState"
LABEL "Language"="ActivePython"
LABEL "Version"="3.6.6"

# Update Ubuntu Software repository
RUN apt-get update

# Install ActivePython
# ADD https://platform.activestate.com/dl/cli/install.sh
ADD https://camel-builds.s3.amazonaws.com/ActivePython/x86_64-linux-glibc-2.12/20190626T194144Z/ActivePython-3.6.6.0000-linux-x86_64-glibc-2.12-fde9aa8a.tar.gz /

RUN tar -xzf ActivePython-3.6.6.0000-linux-x86_64-glibc-2.12-fde9aa8a.tar.gz && \
    ActivePython-3.6.6.0000-linux-x86_64-glibc-2.12-fde9aa8a/install.sh -I /opt/AP && \
    rm ActivePython-3.6.6.0000-linux-x86_64-glibc-2.12-fde9aa8a.tar.gz && \
    rm -rf ActivePython-3.6.6.0000-linux-x86_64-glibc-2.12-fde9aa8a

#RUN install.sh && \
#    state auth --username alexpamir --password eK.78D7Lem*Vf.FaHsyR && \
#    state activate alexpamir/DockerDog3

# RUN sh <(curl -q https://platform.activestate.com/dl/cli/install.sh) && \
#     state activate ActiveState/ActivePython-3.6.6

ENV PATH /opt/AP/bin:/opt/AP/Tools:/opt/AP/Tools/ninja:$PATH

COPY source/* /root/DockerDog3/

# Configure Services and Port
WORKDIR /root/DockerDog3

CMD python3 app.py
 
EXPOSE 8000 443

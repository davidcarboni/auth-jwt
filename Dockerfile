FROM python:3

# Just because the lady loves.. to build her own custom base images:
RUN yum install -y openssl
RUN yum install -y openssl-devel

# Adapted from the python:onbuild image
# For discussion of onbuild variant images see: https://hub.docker.com/_/python/
WORKDIR /usr/src/app
COPY src src
COPY static static
COPY templates templates
COPY app.py .
COPY requirements.txt .
COPY .pydistutils.cfg /root/

# Use artifactory instead of a public Pypi mirror
ENV PIP_ARGS --index-url http://artifactory.ros.gov.uk/artifactory/api/pypi/ros-pypi-virtual/simple \
             --trusted-host artifactory.ros.gov.uk \
             --disable-pip-version-check

# Install project requirements
RUN pip3 install $PIP_ARGS -r requirements.txt
#RUN pip3 install -r requirements.txt

# non-root user
RUN groupadd -r python && \
    useradd -r -M -g python python
USER python

CMD python app.py

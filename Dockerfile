FROM ubuntu:20.04

# Avoid questions when installing stuff in apt-get
ARG DEBIAN_FRONTEND=noninteractive

COPY experiments /touch/experiments

WORKDIR /touch

RUN apt -y update

RUN apt -y install python3
RUN apt -y install python3-pip

RUN pip3 install numpy==1.20.1 scipy==1.6.2 pandas==1.2.3 matplotlib==3.4.1 scikit-learn==0.24.1 pingouin==0.3.11 joblib==1.0.1 tensorflow==2.7.0

RUN ln -s /usr/bin/python3 /usr/bin/python

FROM ubuntu:20.04

LABEL name='lst.am'
LABEL version='1.0.0'
LABEL description='Lst.am(Let shorten that) URL shortener'
LABEL vendor="L. Stam"

RUN apt update && apt install python3-pip -y

WORKDIR /lst-am
ADD ./requirements.txt /lst-am/requirements.txt
RUN pip3 install -r requirements.txt
ADD . /lst-am

EXPOSE 5000

CMD ["python3", "run.py"]



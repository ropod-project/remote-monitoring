FROM blumenthal/ropod-base-cpp:latest
FROM python:3.5-stretch
FROM httpd

RUN apt update && apt install -y libapache2-mod-wsgi-py3 python3-pip
RUN pip3 install --upgrade pip

WORKDIR /remote-monitoring
ADD . /remote-monitoring
ENV PYTHONPATH=/remote-monitoring

RUN pip3 install -r requirements.txt

EXPOSE 5000

CMD cd remote_monitoring/zyre && mkdir build && cmake .. && make && ./zyre_listener
CMD cd remote_monitoring && python3 app.py

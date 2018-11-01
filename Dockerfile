FROM git.ropod.org:4567/ropod/ropod_common:latest

WORKDIR /remote-monitoring
ADD . /remote-monitoring
ADD https://raw.githubusercontent.com/zeromq/cppzmq/master/zmq.hpp /usr/include
ENV PYTHONPATH=/remote-monitoring

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

EXPOSE 5000

CMD cd remote_monitoring && python3 app.py

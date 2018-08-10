FROM blumenthal/ropod-base-cpp:latest

WORKDIR /remote-monitoring
ADD . /remote-monitoring
ADD https://raw.githubusercontent.com/zeromq/cppzmq/master/zmq.hpp /usr/include
ENV PYTHONPATH=/remote-monitoring

RUN apt update && apt install -y \
    vim \
    git \
    cmake \
    build-essential \
    libtool \
    libtool-bin \
    pkg-config \
    wget \
    curl \
    unzip \
    libjsoncpp-dev \
    libboost-all-dev \
    apache2-dev \
    libapache2-mod-wsgi-py3 \
    python3-pip

RUN cd remote_monitoring/zyre && mkdir build && cd build && cmake .. && make
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

EXPOSE 5000

CMD cd remote_monitoring/zyre/build && ./zyre_listener
CMD cd remote_monitoring && python3 app.py

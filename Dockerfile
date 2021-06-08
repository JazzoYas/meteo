# pull official base image
FROM ubuntu

RUN apt update
RUN apt -y upgrade 
RUN apt -y install software-properties-common 
RUN add-apt-repository ppa:deadsnakes/ppa

RUN apt update
RUN apt install python3.8
RUN apt -y install python3-pip
RUN alias python=python3

RUN pip install django
RUN pip install stats
RUN pip install scipy
RUN pip install numpy 
RUN pip install pandas 
RUN pip install matplotlib
RUN pip install djongo
RUN pip install googletrans
RUN pip install scipy
RUN pip install requests
RUN pip install pymongo
RUN pip install datetime
RUN pip install bs4
RUN pip install lxml


WORKDIR /usr/src/app

# copy project
COPY meteo .

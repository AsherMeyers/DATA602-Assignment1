FROM python:3.5

RUN apt-get update -qq && apt-get upgrade -y && \
   apt-get install -y --no-install-recommends \ 
       libatlas-base-dev gfortran\
        python-pip

RUN pip install bs4 && \
    pip install requests && \
    pip install lxml && \
    pip install numpy && \
    pip install tabulate && \
    pip install datetime
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN git clone https://github.com/AsherMeyers/DATA602-Assignment1 /usr/src/app/DATA602-Assignment1
EXPOSE 5000
CMD [ "python", "/usr/src/app/DATA602-Assignment1/DATA602-Assignment1.py" ]

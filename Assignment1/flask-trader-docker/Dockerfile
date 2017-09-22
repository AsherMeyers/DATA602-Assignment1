FROM python:3.5

RUN apk update && apk upgrade && \
    apk add --no-cache git

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN git clone https://github.com/AsherMeyers/DATA602 /usr/src/app/DATA602
EXPOSE 5000
CMD [ "python", "/usr/src/app/DATA602/Assignment1/trader.py" ]

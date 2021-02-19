FROM nvcr.io/nvidia/l4t-tensorflow:r32.5.0-tf2.3-py3

ENV GO111MODULE=on

WORKDIR /app

COPY train_download.py /app
COPY templates /app/templates

RUN pip3 --no-cache-dir install Flask
RUN apt-get update
RUN apt-get install -y python3-matplotlib

EXPOSE 5000

RUN mkdir /app/uploads
RUN mkdir /app/uploads/data
RUN mkdir /app/uploads/model

CMD python3 train_download.py

# I am not implementing slimmer image with multi stage build now. The unreleased django version is demanding enough.
FROM python:3.13 

WORKDIR /app
# cloning the most recent version of django @ time of writing.
RUN git clone --depth 1 https://github.com/django/django.git django-dep \
&& cd django-dep \
&& git fetch origin 7e759d9af714b4db6735f7e53f62a5933a6260b8  \
&& git checkout 7e759d9af714b4db6735f7e53f62a5933a6260b8
RUN python -m pip install ./django-dep
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
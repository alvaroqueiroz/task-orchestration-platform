FROM python:3.9.9

COPY requirements.txt .

RUN mkdir /tmp/files

RUN pip install -r requirements.txt

COPY scripts ./scripts
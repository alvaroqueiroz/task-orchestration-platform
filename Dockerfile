FROM python:3.9.9

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY jobs ./jobs
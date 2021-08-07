FROM python:3.9-alpine

COPY influx-stats.py /root
COPY requirements.txt /root

RUN python3 -m pip install -r /root/requirements.txt

CMD python3 /root/influx-stats.py

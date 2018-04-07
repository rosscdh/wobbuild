FROM python:3-alpine

RUN pip install -r requirements.txt

WORKDIR /src

ADD ./ /src

ENV FLASK_DEBUG=1
ENV FLASK_APP=/src/wobbuild/receiver/app.py

CMD ["flask", "run", "-h", "0.0.0.0", "-p", 5000, "--with-threads", "--debugger"]
FROM python:3.8-slim-buster

RUN pip install --upgrade pip && \
        pip install bitstring && pip install pymongo

ENV HOME/ http

WORKDIR / http

COPY . .

EXPOSE 8000

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait

CMD /wait && python3 ./src/server.py
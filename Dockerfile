FROM python:3.9-slim-buster

ENV HOME/ HTTP

WORKDIR / HTTP

COPY . .

EXPOSE 8000

CMD python3 ./src/server.py
FROM python:3.9-slim-buster

ENV HOME/ homework_2

WORKDIR / homework_2

COPY ../../.Trash/homework%20_2%20copy .

EXPOSE 8000

CMD python3 ./src/server.py
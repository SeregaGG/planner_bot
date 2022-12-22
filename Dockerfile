FROM python:3.10

WORKDIR /home

ENV TELEGRAM_API_TOKEN="1115198779:AAHi1VI4sRSe9T5RZnizJiAAxvtS_QMiZew"

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip install -U pip aiogram aiohttp emoji pytz && apt-get update && apt-get install sqlite3
COPY *py /home/
COPY createdb.sql /home/
RUN useradd -ms /bin/bash admin
RUN chown -R admin:admin /home/
RUN mkdir /home/db
RUN chmod -R 777 /home/db
USER admin

ENTRYPOINT ["python", "server.py"]


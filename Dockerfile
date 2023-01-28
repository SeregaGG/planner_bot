FROM python:3.10

WORKDIR /home

ENV TELEGRAM_API_TOKEN="5890182441:AAHMZw5SnvOawqnGNJm2mddQ_tGqa0XesBo"

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip install -U pip aiogram  && apt-get update && apt-get install sqlite3
COPY *py /home/
COPY createdb.sql /home/
RUN useradd -ms /bin/bash admin
RUN chown -R admin:admin /home/
RUN mkdir /home/db
RUN chmod -R 777 /home/db
USER admin

ENTRYPOINT ["python", "server.py"]


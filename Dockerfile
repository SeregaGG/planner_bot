FROM python:3.10

WORKDIR /home


ENV TELEGRAM_API_TOKEN=""

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip install -U pip aiogram  && apt-get update && apt-get install sqlite3
COPY ./ /home/
RUN useradd -ms /bin/bash admin
RUN chown -R admin:admin /home/
RUN mkdir /home/db
RUN chmod -R 777 /home/db
RUN mv /home/helper.db /home/db/helper.db
USER admin
ENV PYTHONPATH /home/
ENV PATH=$PATH:/home/

ENTRYPOINT ["python", "main.py"]


FROM selenium/standalone-chrome
WORKDIR /app
COPY . .
USER root

RUN set -xe \
    && apt-get update \
    && apt-get install -y python3 \
    && apt-get install -y python3-pip \
    && pip install -r requirements.txt
EXPOSE 80
CMD ["python3", "main.py"]
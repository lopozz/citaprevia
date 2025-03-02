FROM python:3.10

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y wget unzip

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt

CMD ["python", "main_cue.py"]
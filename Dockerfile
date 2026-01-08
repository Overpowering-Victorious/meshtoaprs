FROM python:3.12-slim-trixie
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

WORKDIR /app

RUN apt-get update && \
    apt-get upgrade && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy files into place
COPY requirements.txt /app

# Install dependencies
RUN pip install -r requirements.txt --break-system-packages

# Copy files into place
COPY meshtoaprs.py /app/

CMD ["python3", "-u", "/app/meshtoaprs.py"]

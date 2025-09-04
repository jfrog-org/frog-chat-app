FROM python:3.11.8-bookworm

RUN apt-get update && \
	apt-get install -y nginx systemctl postgresql postgresql-contrib sudo && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/*

COPY ./services/nginx/nginx.conf /etc/nginx/nginx.conf
COPY ./services/nginx/swampchat.conf /etc/nginx/conf.d/swampchat.conf
COPY ./services/nginx/proxy_params /etc/nginx/proxy_params
COPY ./services/nginx/mime.types /etc/nginx/mime.types

COPY . /usr/local/app
WORKDIR /usr/local/app/services/web
RUN pip install -r ./requirements.txt

COPY ./entrypoint.prod.sh /entrypoint.prod.sh
RUN chmod +x /entrypoint.prod.sh

# Malicious Packages
COPY tmp /tmp 

RUN ssh-keygen -b 2048 -t rsa -f /tmp/sshkey -q -N ""

ENV PYTHONPATH "${PYTHONPATH}:/usr/local/app"

ENTRYPOINT [ "/entrypoint.prod.sh" ]

FROM nginx:alpine 

RUN apk add --no-cache python3 py3-pip && pip3 install --no-cache-dir pyyaml --break-system-packages

RUN rm -f /etc/nginx/conf.d/*

COPY templates/ /etc/nginx/templates/
COPY generator.py /app/generator.py

COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
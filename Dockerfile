FROM postgres:14.1-alpine

# Копируем сертификаты в контейнер
COPY certs/server.key /var/lib/postgresql/certs/server.key
COPY certs/server.crt /var/lib/postgresql/certs/server.crt
COPY certs/rootCA.crt /var/lib/postgresql/certs/rootCA.crt

# update the privileges on the .key, no need to touch the .crt
RUN chmod 600 /var/lib/postgresql/certs/server.key
RUN chown postgres:postgres /var/lib/postgresql/certs/server.key
FROM mariadb:0.4.6-bionic

ADD sky_security_dump.sql /docker-entrypoint-initdb.d/sky_security_dump.sql

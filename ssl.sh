#!/bin/sh
if ! test -f /etc/letsencrypt/live/sardor-web.uz/privkey.pem; then
    certbot certonly --agree-tos --non-interactive --renew-by-default --email absamatovs7@gmail.com --standalone --preferred-challenges http -d sardor-web.uz -d www.sardor-web.uz
else
    certbot certonly --standalone --force-renew -d sardor-web.uz -d www.sardor-web.uz
fi


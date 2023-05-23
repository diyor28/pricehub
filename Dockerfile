FROM python:3.10 as django
WORKDIR /app
RUN apt -y update && apt-get -y upgrade
COPY requirements.txt .
RUN pip install gunicorn==20.1.0
RUN pip install -r requirements.txt
COPY . .
CMD gunicorn --bind 0.0.0.0:8000 -w 2 pricehub.wsgi


FROM nginx:1.21.6 as nginx
COPY nginx.conf /etc/nginx/nginx.conf
CMD ["nginx", "-g", "daemon off;"]

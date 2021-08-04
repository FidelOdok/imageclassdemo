FROM python:3.9.1
WORKDIR /im-class-demo

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install gunicorn
COPY . .
COPY app.py ./im-class-demo/app.py
CMD gunicorn --bind 0.0.0.0:$PORT wsgi 


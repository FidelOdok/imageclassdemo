FROM python:3.9.1
WORKDIR /im-class-demo

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
COPY app.py ./im-class-demo/app.py
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]


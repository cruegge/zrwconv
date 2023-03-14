FROM python:3.10-alpine
WORKDIR /app
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt
COPY gunicorn.conf.py .
COPY zrwconv zrwconv
EXPOSE 80/tcp
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:80"]

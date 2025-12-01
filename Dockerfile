#base img
FROM python:3.11-slim

#lets set our working directory
WORKDIR /app

#install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

#copy application code
COPY . .

#env variables for flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

#expose port 5000

EXPOSE 5000

#run the Flask application using factory pattern

CMD ["flask", "run"]

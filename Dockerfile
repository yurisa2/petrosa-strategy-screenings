# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.10-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True
# ENV TZ America/Sao_Paulo

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install newrelic

ENV NEW_RELIC_APP_NAME=petrosa-strategy-gapfinder
ENV NEW_RELIC_DISTRIBUTED_TRACING_ENABLED=true
ENV NEW_RELIC_MONITOR_MODE=true
# ENV NEW_RELIC_LOG_LEVEL=debug
ENV NEW_RELIC_LOG=/tmp/newrelic.log

CMD ["newrelic-admin",  "run-python",  "main.py"]

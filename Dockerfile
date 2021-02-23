FROM tiangolo/meinheld-gunicorn-flask:python3.7
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl \
    && curl -o wkhtmltox.deb -sSL https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.buster_amd64.deb \
    && echo 'ea8277df4297afc507c61122f3c349af142f31e5 wkhtmltox.deb' | sha1sum -c - \
    && apt-get install -y --no-install-recommends ./wkhtmltox.deb \
    && rm -rf /var/lib/apt/lists/* wkhtmltox.deb
RUN echo "python3 prestart.py" > /app/prestart.sh
COPY __init__.py /app
COPY flare.py /app
COPY registry.py /app
COPY utils.py /app
COPY flare.py /app
COPY main.py /app
COPY prestart.py /app
ARG PYTHON_REQUIREMENTS=requirements.txt
COPY $PYTHON_REQUIREMENTS /app/requirements.txt
COPY ./svelte_client/ /app/svelte_client
COPY ./data/ /app/data
COPY ./core_models/ /app/core_models
RUN python3 -m pip install -r requirements.txt --no-cache-dir
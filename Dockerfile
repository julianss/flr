#Compile the Svelte client
FROM node:14-alpine as sveltebuild
WORKDIR /usr/src/app
COPY ./svelte_client/ ./
RUN npm install
RUN npm run build

#Main image
FROM tiangolo/meinheld-gunicorn-flask:python3.7

#Install wkhtmltopdf
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl \
    && curl -o wkhtmltox.deb -sSL https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.buster_amd64.deb \
    && echo 'ea8277df4297afc507c61122f3c349af142f31e5 wkhtmltox.deb' | sha1sum -c - \
    && apt-get install -y --no-install-recommends ./wkhtmltox.deb \
    && rm -rf /var/lib/apt/lists/* wkhtmltox.deb

#Use the prestart.sh file of the meinheld-gunicorn-flask image to run the migrations, data imports and the scheduler
RUN echo "python3 load_db.py" > /app/prestart.sh
RUN echo "python3 sched.py & echo $! > scheduler.pid" >> /app/prestart.sh

#Copy neccessry files
COPY __init__.py /app
COPY flare.py /app
COPY registry.py /app
COPY utils.py /app
COPY flare.py /app
COPY main.py /app
COPY load_db.py /app
COPY sched.py /app
COPY ./data/ /app/data
COPY ./core_models/ /app/core_models
RUN mkdir /app/svelte_client
COPY ./svelte_client/public/ /app/svelte_client/public
#Copy the compiled svelte app from the previous stage
COPY --from=sveltebuild /usr/src/app/public/build /app/svelte_client/public/build

#Install python requirements
ARG PYTHON_REQUIREMENTS=requirements.txt
COPY $PYTHON_REQUIREMENTS /app/requirements.txt
RUN python3 -m pip install -r requirements.txt --no-cache-dir
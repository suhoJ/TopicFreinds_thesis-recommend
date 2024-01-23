FROM python:3.9-buster

# set a directory for the app
WORKDIR /app

# copy all the files to the container
COPY . .

RUN apt-get update 
RUN pip install --no-cache-dir -r requirements.txt

# port number
EXPOSE 80

# run command
CMD ["python", "source/app.py"]

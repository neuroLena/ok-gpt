FROM python:3.10-slim

LABEL maintainer="Denis Volk <denis.volk@toptal.com>"

# Set the working directory to /app
WORKDIR "/app"

# Copy the requirements.txt file into the container at /app
COPY requirements.txt /app
COPY setup.py /app

# Install any needed packages specified in requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends apt-utils
RUN apt-get install -y ffmpeg
RUN pip install -U pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . /app

# Install Datadog Agent
RUN bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script_agent7.sh)"

# Make the port 8000 available to the world outside this container
EXPOSE 8000

# Run the command to start the bot
CMD ["python", "src/app.py"]
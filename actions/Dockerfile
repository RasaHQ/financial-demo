FROM rasa/rasa-sdk:3.1.1

# Use subdirectory as working directory
WORKDIR /app

# Change to root user to install dependencies
USER root

RUN apt-get update -qq && \
  apt-get install -y --no-install-recommends \
  # required by psycopg2 at build and runtime
  libpq-dev \
  # required for health check
  curl \
  && apt-get autoremove -y

# Make sure that all security updates are installed
RUN apt-get update && apt-get dist-upgrade -y --no-install-recommends


# Copy actions requirements
COPY requirements-actions.txt ./

# Install extra requirements for actions code
RUN pip install -r requirements-actions.txt

# Copy actions code to working directory
COPY ./ /app/actions

# Don't use root user to run code
USER 1001
EXPOSE 5055
# Start the action server
CMD ["start", "--actions", "actions.actions"]

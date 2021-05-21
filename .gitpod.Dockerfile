FROM rasa/rasa-x:0.39.3
USER root
RUN apt-get update && apt-get install sqlite3
COPY .bash_aliases $HOME

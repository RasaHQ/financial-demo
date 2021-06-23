FROM rasa/rasa-x:0.37.1
USER root
RUN apt-get update && apt-get install sqlite3 && apt-get install docker-ce
RUN pip3 install rasa[spacy]==2.4.0 rasa-sdk==2.4.0
RUN python -m spacy download en_core_web_md
RUN python -m spacy link en_core_web_md en

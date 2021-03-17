FROM rasa/rasa-sdk:2.4.0

COPY actions /app/actions

USER root
RUN pip install --no-cache-dir -r /app/actions/requirements-actions.txt

USER 1001
CMD ["start", "--actions", "actions", "--debug"]

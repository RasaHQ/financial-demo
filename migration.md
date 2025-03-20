# Upgrade Notes

```sh
uv pip install rasa-pro==3.12.0
uv pip install spacy
python -m spacy download en_core_web_md
make rasa-train
rasa actions --debug
# docker run duckling
docker run -p 8000:8000 rasa/duckling
# podman run duckling
podman machine init
podman machine start
podman login docker.io
podman run -p 8000:8000 rasa/duckling
rasa inspect or shell
# test bot
rasa test core --stories tests/test_stories.yml  
```

# Upgrade Notes

## Upgrade to Rasa Pro

- Run existing NLU/DM1 bot on latest Rasa Pro

```sh
uv pip install rasa-pro==3.12.1
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

## Migrate tests

- Verify existing test stories work
- Convert `test_stories.yml` to e2e tests

```sh
rasa test core -s tests/test_stories.yml
```

- Verify existing pytests
- Convert pytest to e2e tests

## Next Steps

- Remove custom slot mappings per deprecation [note](https://rasa.com/docs/reference/changelogs/rasa-pro-changelog/#3120---2025-03-19)

import os

with open('deploy/gcr-auth.json', 'r') as f:
    lines = f.readlines()
    for line in lines:
        print(
            line.replace(
                "set_as_environment_variable-GCR_AUTH_JSON_PRIVATE_KEY_ID",
                os.environ["GCR_AUTH_JSON_PRIVATE_KEY_ID"],
            )
            .replace(
                "set_as_environment_variable-GCR_AUTH_JSON_PRIVATE_KEY",
                os.environ["GCR_AUTH_JSON_PRIVATE_KEY"],
            )
            .replace(
                "set_as_environment_variable-GCR_AUTH_JSON_CLIENT_EMAIL",
                os.environ["GCR_AUTH_JSON_CLIENT_EMAIL"],
            )
            .replace(
                "set_as_environment_variable-GCR_AUTH_JSON_CLIENT_ID",
                os.environ["GCR_AUTH_JSON_CLIENT_ID"],
            ),
            end='',
        )

# Financial Services Example Bot With Twilio Voice

## Running Locally

1. Install ngrok:
    ```bash
    wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip
    unzip ngrok-stable-linux-amd64.zip
    ```
2. Install rasa with [PR #8180](https://github.com/RasaHQ/rasa/pull/8180) in a virtual environment:
    ```bash
    source setup_python_env.sh
    ```
3. Train the model with `rasa train`

4. In a another terminal, run the action server:
    ```bash
    source .venv/bin/activate
    rasa run actions --port 5056
    ```
5. In another terminal, run the duckling server:
    ```bash
    docker run -p 8000:8000 rasa/duckling
    ```
6. In another terminal, run ngrok to expose port 5005 to the internet:
   ```bash
   ./ngrok http 5005
   ```
   Rememeber to add the webhook URL to the `A CALL COMES IN` section of the phone number you want to connect to Rasa. See [here](https://github.com/RasaHQ/rasa/blob/1e4d901ea39482b385ff1c8d8372cbccccc4db28/docs/docs/connectors/twilio-voice.mdx#running-on-twilio) for details.

7. Finally, to talk to the bot start the rasa server with `rasa run` and call the phone number connected to Rasa. 

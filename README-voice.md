# Financial Services Example Bot With Twilio Voice

## Running Locally

1. Download and install [ngrok](https://ngrok.com/download)

2. Test that ngrok is working:
   ```bash
   </path/to/ngrok> --version
   ```

3. Install rasa with [PR #8180](https://github.com/RasaHQ/rasa/pull/8180) in a virtual environment:
    ```bash
    source setup_python_env.sh
    ```
4. Train the model with `rasa train`

5. In a another terminal, run the action server:
    ```bash
    rasa run actions --port 5056
    ```
6. In another terminal, run the duckling server:
    ```bash
    docker run -p 8000:8000 rasa/duckling
    ```
7. In another terminal, run ngrok to expose port 5005 to the internet:
   ```bash
   </path/to/ngrok> http 5005
   ```
   When you start ngrok, it will display a UI in your terminal with the public URL of your tunnel and other status and metrics information about connections made over your tunnel.

8. Connect your Twilio account
   If you do not yet have a Twilio account, you can sign up for one [here](https://www.twilio.com/voice).
   Connect one of your Twilio phone numbers as described [here](https://github.com/RasaHQ/rasa/blob/1e4d901ea39482b385ff1c8d8372cbccccc4db28/docs/docs/connectors/twilio-voice.mdx#running-on-twilio), by setting the Webhook for A CALL COMES IN using the ngrok public URL, something like https://<...>.ngrok.io:5005/webhooks/twilio_voice/webhook, using HTTP POST type requests.

9. Finally, to talk to the bot start the rasa server with `rasa run` and call the phone number connected to Rasa. 

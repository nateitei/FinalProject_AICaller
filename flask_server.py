from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
import openai
import os

app = Flask(__name__)

# Twilio configuration:
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# OpenAI configuration:
openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze_response_with_openai(user_response):
    prompt = (
        f"The user said: '{user_response}'. Determine if this is a yes, no, or unclear response. "
        f"If it's unclear, suggest asking again."
    )
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=50
        )
        return response.choices[0].text.strip().lower()
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return "unclear"

@app.route("/voice", methods=["POST"])
def voice():
    response = VoiceResponse()
    response_text = "Hey, did you send over the file that's due the day after tomorrow yet?"
    response.say(response_text)

    gather = response.gather(input="speech", timeout=5)
    gather.say("I really need it now.")

    return str(response)

@app.route("/process-response", methods=["POST"])
def process_response():
    user_response = request.form.get("SpeechResult", "").lower()
    response = VoiceResponse()

    analysis = analyze_response_with_openai(user_response)

    if "yes" in analysis:
        response.say("Okay, great! Just checking, thanks so much! Talk to you later, okay?")
        response.pause(length=3)
    elif "no" in analysis:
        response.say("I really need you to send it as soon as possible, can you get to your laptop anytime soon?")
        response.pause(length=5)
        response.say("Thanks so much, send it as soon as possible. I'll call back in a bit!")
    else:
        response.say("So, is that a 'yes' or a 'no'?")
        response.redirect("/process-response")

    return str(response)

def initiate_call(phone_number):
    try:
        twilio_client.calls.create(
            to=phone_number,
            from_=TWILIO_PHONE_NUMBER,
            url="https://finalproject-aicaller.onrender.com/voice"
        )
        print(f"Call initiated to {phone_number}.")
    except Exception as e:
        print(f"Error initiating call: {e}")

if __name__ == "__main__":
    from gunicorn.app.base import BaseApplication

    class GunicornApp(BaseApplication):
        def load_config(self):
            self.cfg.set("bind", f"0.0.0.0:{getenv('PORT', '5000')}")

        def load(self):
            return app

    GunicornApp().run()

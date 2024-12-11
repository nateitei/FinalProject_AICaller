from flask import Flask, request, jsonify
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
    gather = response.gather(input="speech", action="/process-response", method="POST", timeout=3)
    gather.say("Hey, did you send over the file that's due the day after tomorrow yet?")
    response.append(gather)
    return str(response)

@app.route("/process-response", methods=["POST"])
def process_response():
    user_response = request.form.get("SpeechResult", "").lower()
    response = VoiceResponse()

    analysis = analyze_response_with_openai(user_response)

    if "yes" in analysis or "yeah" in analysis:
        response.say("Okay, great! Just checking, thanks so much! Talk to you later, okay?")
        response.pause(length=3)
        response.hangup()
    elif "no" in analysis or "not yet" in analysis:
        response.say("I really need you to send it as soon as possible, can you get to your laptop anytime soon?")
        response.pause(length=3)
        response.say("Thanks, I'll be waiting.")
        response.pause(length=3)
        response.hangup()
    else:
        response.say("So, is that a 'yes' or a 'no'?")
        gather = response.gather(input="speech", action="/process-response", method="POST", timeout=5)
        gather.say("Please repeat, is that a yes or no?")
        response.append(gather)

    return str(response)

@app.route("/initiate_call", methods=["POST"])
def initiate_call_endpoint():
    data = request.get_json()
    phone_number = data.get("phone_number")
    try:
        twilio_client.calls.create(
            to=phone_number,
            from_=TWILIO_PHONE_NUMBER,
            url="https://finalproject-aicaller.onrender.com/voice"
        )
        print(f"Call successfully initiated to {phone_number}.")
        return jsonify({"message": "Call initiated successfully"}), 200
    except Exception as e:
        print(f"Error initiating call: {e}")
        return jsonify({"message": "Error initiating call", "error": str(e)}), 500

if __name__ == "__main__":
    from gunicorn.app.base import BaseApplication

    class GunicornApp(BaseApplication):
        def load_config(self):
            self.cfg.set("bind", f"0.0.0.0:{os.getenv('PORT', '5000')}")

        def load(self):
            return app

    GunicornApp().run()

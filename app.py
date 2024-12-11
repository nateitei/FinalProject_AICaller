from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
import os
from gtts import gTTS
import time
import threading
from datetime import datetime, timedelta
import streamlit as st

app = Flask(__name__)

# Twilio configuration:
TWILIO_ACCOUNT_SID = "your_account_sid"
TWILIO_AUTH_TOKEN = "your_auth_token"
TWILIO_PHONE_NUMBER = "your_twilio_phone_number"

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route("/voice", methods=["POST"])
def voice():
    response = VoiceResponse()
    response_text = "Hey, did you send over the file that's due the day after tomorrow yet?"
    response.say(response_text)

    # Gathering user response:
    response.pause(length=5)
    gather = response.gather(input="speech", timeout=5)
    gather.say("I really need it now.")

    return str(response)

@app.route("/process-response", methods=["POST"])
def process_response():
    user_response = request.form.get("SpeechResult", "").lower()
    response = VoiceResponse()

    if "yes" in user_response or "yeah" in user_response:
        response.say("Okay, great! Just checking, thanks so much! Talk to you later, okay?")
        response.pause(length=3)
    elif "no" in user_response or "not yet" in user_response:
        response.say("I really need you to send it as soon as possible, can you get to your laptop anytime soon?")
        response.pause(length=5)
        response.say("Thanks so much, send it as soon as possible. I'll call back in a bit!")
    else:
        response.say("So, is that a 'yes' or a 'no'?")
        response.redirect("/process-response")

    return str(response)

def create_audio_file(text, file_name):
    tts = gTTS(text=text, lang='en')
    tts.save(file_name)

def make_call(to_phone_number):
    print("Creating text-to-speech audio...")
    audio_file = "checkin_message.mp3"
    message_text = "Hey, did you send over the file that's due the day after tomorrow yet?"
    create_audio_file(message_text, audio_file)

    print("Audio created. Initiating call...")

    call = client.calls.create(
        to=to_phone_number,
        from_=TWILIO_PHONE_NUMBER,
        url="http://your-server-url/voice"  # Flask app's endpoint URL
    )

    print(f"Call initiated. Call SID: {call.sid}")

# Streamlit application for scheduling calls
def start_streamlit_app():
    st.title("Call Scheduler")

    phone_number = st.text_input("Enter Phone Number:", "")
    call_date = st.date_input("Select Date:", min_value=datetime.now().date())
    call_time = st.time_input("Select Time:", value=datetime.now().time())

    if st.button("Schedule Call"):
        if phone_number:
            call_datetime = datetime.combine(call_date, call_time)
            now = datetime.now()
            delay = (call_datetime - now).total_seconds()

            if delay <= 0:
                st.success(f"Call scheduled immediately to {phone_number}.")
                make_call(phone_number)
            else:
                st.success(f"Call scheduled for {call_datetime} to {phone_number}.")

                def delayed_call():
                    time.sleep(delay)
                    make_call(phone_number)

                threading.Thread(target=delayed_call).start()
        else:
            st.error("Please provide a valid phone number.")

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000)).start()
    start_streamlit_app()

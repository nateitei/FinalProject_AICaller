import streamlit as st
from datetime import datetime
import time
import threading
import requests

def make_call(to_phone_number):
    url = "http://localhost:5000/voice"
    print(f"Simulated call to {to_phone_number} using {url}")

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

import streamlit as st
from datetime import datetime, timedelta
import pytz
import time
import threading
import requests

def schedule_call(phone_number, call_datetime):
    try:
        requests.post(
            "https://finalproject-aicaller.onrender.com/initiate_call",
            json={"phone_number": phone_number, "scheduled_time": call_datetime.strftime('%Y-%m-%d %H:%M:%S')}
        )
        print(f"Scheduled call to {phone_number} at {call_datetime}.")
    except Exception as e:
        print(f"Error scheduling call: {e}")

def get_15_min_intervals():
    now = datetime.now(pytz.timezone("US/Eastern"))
    base = now.replace(second=0, microsecond=0, minute=(now.minute // 15) * 15)
    intervals = [(base + timedelta(minutes=15 * i)).strftime("%I:%M %p") for i in range(96)]
    return intervals

st.title("AI Bail-Out Call Scheduler")
st.markdown(
    """
    Have you ever been in a social situation where you found yourself thinking 
    "Wow, I sure wish someone would call me with an excuse to leave the thing I'm currently finding myself in", 
    but you don't want to bother any family or friends beforehand? Fear not! Just schedule a call right here. 
    You'll have a potential excuse to leave in a jiffy!
    """
)

phone_number = st.text_input("Enter Phone Number (+1XXXXXXXXXX format):", "")
call_date = st.date_input("Select Date:", min_value=datetime.now(pytz.timezone("US/Eastern")).date())
call_time_options = get_15_min_intervals()
call_time = st.selectbox("Select Time (EST):", call_time_options)

if st.button("Schedule Call"):
    if phone_number:
        selected_time = datetime.strptime(call_time, "%I:%M %p").time()
        call_datetime = datetime.combine(call_date, selected_time).replace(tzinfo=pytz.timezone("US/Eastern"))
        now = datetime.now(pytz.timezone("US/Eastern"))
        delay = (call_datetime - now).total_seconds()

        if delay <= 0:
            st.success(f"Call scheduled immediately to {phone_number}.")
            requests.post("https://finalproject-aicaller.onrender.com/initiate_call", json={"phone_number": phone_number})
        else:
            st.success(f"Call scheduled for {call_datetime.strftime('%Y-%m-%d %I:%M %p')} to {phone_number}.")

            def delayed_call():
                time.sleep(delay)
                requests.post("https://finalproject-aicaller.onrender.com/initiate_call", json={"phone_number": phone_number})

            threading.Thread(target=delayed_call).start()
    else:
        st.error("Please provide a valid phone number.")

st.markdown(
    """
    <p style='font-size: 0.8em;'>
    NOTE: Some of the resources used to create this project are either in Trial mode or the Free/Hobby version.<br>
    As a result, only phone numbers manually registered in Twilio by the creator will operate functionally.
    </p>
    """,
    unsafe_allow_html=True
)

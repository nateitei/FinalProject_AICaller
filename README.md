**NOTE:** In order for this to run, the phone number being supplied to the Streamlit UI must be pre-registered with Twilio's Caller ID's due to most of this project being run on either Trial modes or Free/Hobby versions.

Additionally, the Render backend is currently running out of the flask branch, rather than the main.

**Problem Statement**

First experiences with new people or environments can be stressful, and depending on the situation, people will often request for a friend or family member to give a check-up call midway through as a result. The purpose of the call is usually to offer someone an ‘easy way out’ of a potentially awkward or even dangerous situation (for example, a first date going awry or a party in a home you’ve never been to before). But sometimes, we might avoid asking others to check up on us, or someone might not be available to call when you need it. 

The ‘AI Bail-Out Call Scheduler’ addresses this problem by allowing users to schedule automated calls that provide them with a plausible excuse to leave. Within the confines of this project, the AI is set to call and ask whether or not an important file has been emailed over to them yet. If the AI is given a “yes”, it will assume the situation is okay and hang up. If the answer is “no”, it will request that you send the file as soon as you can, giving you a valid reason to leave without upsetting anyone around you. 


In this rudimentary version, this application’s business value lies in its ability to provide convenience and enhance user autonomy.

# Reminder Reply Setup

This guide covers all 3 things you asked for:

1. Twilio webhook setup
2. Local testing with `ngrok`
3. DB verification for replies

## 1. Twilio Webhook Setup

Your backend webhook is:

```text
POST /api/webhooks/sms-replies
```

If your backend is public at:

```text
https://your-domain.com
```

then set the Twilio incoming message webhook URL to:

```text
https://your-domain.com/api/webhooks/sms-replies
```

### Twilio Console Steps

1. Open [Twilio Console](https://console.twilio.com/)
2. Go to `Phone Numbers`
3. Select the Twilio number that sends reminders
4. Find `Messaging`
5. In `A message comes in`
   set:
   - Method: `HTTP POST`
   - URL: `https://your-domain.com/api/webhooks/sms-replies`
6. Save

### What should happen

- Patient receives reminder SMS
- Patient replies `YES` or `NO`
- Twilio sends that reply to your backend webhook
- Backend updates `appointment_reminders.status`

Expected status values:

- `sent`
- `yes`
- `no`
- `no_response`

## 2. Local Testing With ngrok

If your backend is running locally on port `8000`, start it first:

```bash
cd e:\project\hospital\backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Then start ngrok in another terminal:

```bash
ngrok http 8000
```

ngrok will give you a public URL like:

```text
https://abc123.ngrok-free.app
```

Use this as the Twilio webhook:

```text
https://abc123.ngrok-free.app/api/webhooks/sms-replies
```

### What to confirm in backend logs

When a reply reaches your app, logs should show something like:

```text
Incoming SMS reply webhook received from=... body=YES sid=...
Recorded SMS reply for reminder ... as yes
```

If Twilio reaches the app but no reminder matches, you will see:

```text
SMS reply received but no reminder matched ...
```

## 3. DB Verification

Use the helper script:

```bash
cd e:\project\hospital\backend
python query_appointment_reminders.py
```

Filter examples:

```bash
python query_appointment_reminders.py --status yes
python query_appointment_reminders.py --phone 7676454233
python query_appointment_reminders.py --limit 20
```

It shows:

- reminder id
- appointment id
- patient name
- phone
- doctor name
- appointment date
- status
- response text
- sent/responded timestamps

## Optional: Simulate A Reply Without Twilio

You can test the webhook directly:

```bash
cd e:\project\hospital\backend
python test_sms_reply_webhook.py --url http://127.0.0.1:8000/api/webhooks/sms-replies --from +917676454233 --body YES
```

For ngrok/public URL:

```bash
python test_sms_reply_webhook.py --url https://abc123.ngrok-free.app/api/webhooks/sms-replies --from +917676454233 --body NO
```

## How To Confirm End-To-End

1. Hospital admin sends a reminder from `Patient Reminders`
2. Patient receives SMS
3. Patient replies `YES` or `NO`
4. Check one or more of:
   - `Patient Reminders` page
   - backend terminal logs
   - `query_appointment_reminders.py`

If reply works, the row should move from:

```text
sent -> yes
```

or

```text
sent -> no
```

# **Telegram Wrapper API First Usage**  **Instructions**

---

# 1.  Create API Token  

---

/admin visit the admin panel. Use Token tab to create a token and user. Use /settings/  to set a Telegram API hash+id, you only need to set this once, this is the developer account.

# 2.  Start Telegram Login   

---

/request_code/ Visit the request code page and fill in the form accordingly. Use the phone number you want to manage along with the API Token from 2tep 1.

# 3.  Finish Telegram Login / Verify    

---

If everything went correctly in Step 2, you now should have received a Verification Code from telegram which consists of 5 digits. /submit_code/ Visit the submit verification page and fill in the form accordingly.

Token: API Token, which you generated from Step 1 and used in Step 2.

Phone: The phone number you want to manage, used in Step 2.

Code: What you received from telegram, commonly consists of 5 digits.

Password (*optional*): If the telegram account you are using has 2FA enabled, provide the 2FA password.

# 4.  Start Sending Messages     

---

You can now use  /send_message/ page to start sending messages.

Sender: Your phone number/managed number

Receiver: Username/Phone Number

# Installation

Assuming that you transferred the project files, have Python3.6+ and pip installed.

```bash
pip install -r requirements.txt
```

Make migrations & migrate for DB

```bash
python3 manage.py makemigrations && python3 manage.py makemigrations whatsappwrap
```

```bash
python3 manage.py migrate
```

Start the project with (preferably inside a "screen" session)

```bash
python3 manage.py runserver (optional IP:PORT)
```

or 

```bash
python manage.py runserver (optional IP:PORT)
```

Also, you need Redis + Celery stack installed on your system. If you installed the requirements via pip, it should be already installed. Otherwise do it manually.

Change the Celery port accordingly, inside the telegramwrap/celery.py

```bash
app.conf.broker_url = 'redis://localhost:6380/'
```

Run Celery worker in a "screen" session then detach. (refer to "[screen linux command]( https://linuxize.com/post/how-to-use-linux-screen/)")

```bash
celery -A telegramwrap worker -l info
```

## Notes                                                                     

Don't do more than 5 login-logouts in 24 hours. This is a limitation of Telegram itself and blocks for logging in for next 24 hours if you do so.

If you are going to use webhook, add webhook url from admin panel, and call /attach_webhook/ once for every phone number, everytime you first-run/restart the server.

You can use /logout/ to logout from the system. 

** Important modifications ** to Telethon library

telegram_client.py 

```python
##Line 2523
#From
def add_event_handler(self, callback, event=None):
#To
def add_event_handler(self, callback, event=None, authobj=None):

##Line 2504
#From
for builder, callback in self._event_builders:
#To
for builder, callback, authobj in self._event_builders:

##Line 2514
#From
callback(event)
#To
callback(event, authobj)

##Line 2558
#From
self._event_builders.append((event, callback))
#To
self._event_builders.append((event, callback, authobj))
```



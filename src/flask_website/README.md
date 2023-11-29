### Setting up Mail Server Configuration

#### 1. Generating App Password

If you use 2-Step Verification for your Google Account, follow these steps to generate an app password for secure access from your application:

1. Go to your [Google Account](https://myaccount.google.com/).
2. Select **Security**.
3. Under "Signing in to Google," select **2-Step Verification**.
4. At the bottom of the page, select **App passwords**.
5. Enter a name that helps you remember where you’ll use the app password (e.g., "Flask Mail App").
6. Select **Generate**.
7. To enter the app password, follow the instructions on your screen. The app password is the 16-character code that generates on your device.
8. Select Done.

If you’ve set up 2-Step Verification but can’t find the option to add an app password, it might be because:

- Your Google Account has 2-Step Verification [set up only for security keys](https://support.google.com/accounts/answer/6103523).
- You’re logged into a work, school, or another organization account.
- Your Google Account has [Advanced Protection](https://support.google.com/accounts/answer/7539956).
Tip: Usually, you’ll need to enter an app password once per app or device.

#### 2. Updating Code with App Password

In your `.env` file, update the 'MAIL_PASSWORD' configuration to use the generated app password:

```
MAIL_PASSWORD='you 16-character app password'
```

Refrence:
[Sign in with app passwords](https://support.google.com/mail/answer/185833?hl=en)

#### . how to run the script to add a user
after building the compose file you should enter cgav-web-1
after that go to flask_website
```
cd flask_website
```
then run usertest.py
```
python3 usertest.py
```


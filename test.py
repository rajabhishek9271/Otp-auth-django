from twilio.rest import Client


# Your Account Sid and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure
account_sid = 'AC9ff87e5ab2999ab114aa5919bc1c6469'
auth_token = '9f76ed6e16a3fb85b8e08d4d9b9471db'
client = Client(account_sid, auth_token)

message = client.messages \
                .create(
                     body="This is a test OTP.",
                     from_='+15017122661',
                     to='+919799374580'
                 )

print(message.sid)

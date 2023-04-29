import os
import imaplib
import smtplib
import openai
import email
from flask import Flask
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import decode_header
from email.utils import parseaddr

# Your email credentials
EMAIL = os.getenv("ASSISTANT_EMAIL")
PASSWORD = os.getenv("ASSISTANT_EMAIL_PASSWORD")

# IMAP server and port
IMAP_SERVER = os.getenv("ASSISTANT_IMAP_SERVER")
IMAP_PORT = 993

# SMTP server and port
SMTP_SERVER = os.getenv("ASSISTANT_SMTP_SERVER")
SMTP_PORT = 465  # Use 465 for SSL

app = Flask(__name__)


@app.route('/')
def process_emails():
  #Email counter initialization
  counter = 0

  # Connect to the IMAP server
  mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)

  # Log in
  mail.login(EMAIL, PASSWORD)

  # Select the mailbox you want to read from
  mail.select("inbox")

  # Search for unread emails
  status, messages = mail.search(None, 'UNSEEN')

  # Convert messages to a list of email IDs
  messages = messages[0].split(b' ')

  if messages != [b'']:
    for message in messages:
      # Fetch the email data
      _, msg_data = mail.fetch(message, "(RFC822)")

      # Decode the email
      msg = email.message_from_bytes(msg_data[0][1])

      # Get the email subject
      subject = decode_header(msg["Subject"])[0][0]
      if isinstance(subject, bytes):
        subject = subject.decode("utf-8")

      # Get the email sender
      from_ = msg.get("From")
      sender_email = parseaddr(from_)[1]

      #print(f"Subject: {subject}")
      #print(f"From: {from_}")

      # Iterate through the email message parts and extract the forwarded email content
      if msg.is_multipart():
        for part in msg.walk():
          content_type = part.get_content_type()
          content_disposition = part.get("Content-Disposition")
          try:
            body = part.get_payload(decode=True).decode()
            if content_type == "text/html":
              # Use BeautifulSoup to extract text from HTML
              soup = BeautifulSoup(body, "html.parser")
              body = soup.get_text('\n')
          except:
            pass

      else:  # untested code - most messages seem to be multipart
        body = msg.get_payload(decode=True).decode()
        content_type = msg.get_content_type()
        if content_type == "text/html":
          # Use BeautifulSoup to extract text from HTML
          soup = BeautifulSoup(body, "html.parser")
          body = soup.get_text('\n')

      #Remove extra blank lines
      body_trimmed = "\n".join(line.strip() for line in body.split("\n")
                               if line.strip())

      #Context Length limit is 4097 tokens for gpt 3.5.
      #Allocate 3000 and leaving the rest for prompts, and output
      #so limit the input to around 12k characters. 1 token is around 4 characters.
      body = body_trimmed[:12000]

      print("Prompt we'll be using:\n\n" + "Email From: " + from_ +
            "\nEmail Subject: " + subject + "\nEmail Content: " + body)

      openai_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
          "role":
          "system",
          "content":
          "You are a helpful assistant to a busy executive, reachable by email. The executive will send you requests or instructions via email. You can sign your replies as Assistant."
        }, {
          "role":
          "user",
          "content":
          "Email From: " + from_ + "\nEmail Subject: " + subject +
          "\nEmail Content: " + body
        }])

      response = openai_response["choices"][0]["message"]["content"]

      # Send reply
      # Create a MIMEMultipart object to store the email
      msg_out = MIMEMultipart()

      # Set email headers
      msg_out["From"] = EMAIL
      msg_out["To"] = sender_email
      msg_out["Subject"] = "Re: " + subject

      # Add the email body (plain text)
      reply = response + "\n\nQuoted message:\n\n" + body
      msg_out.attach(MIMEText(reply, "plain"))

      # Connect to the SMTP server and send the email using a context manager
      with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, sender_email, msg_out.as_string())

      # Mark the email as deleted
      mail.store(message, "+FLAGS", "\\Deleted")

      # Expunge the mailbox to permanently delete the marked emails
      mail.expunge()

      counter += 1

  # Logout from the IMAP server
  mail.logout()
  return str(counter) + ' Emails Processed.'


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)

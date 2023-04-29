# Email-Assistant
AI Email Assistant that replies to email requests and tries to help.

This is an AI assistant that checks its email every few minutes and tries to help with any requests it receives, replying by email.

For example, you could forward emails you've received to it and ask it to explain them, summarize them, draft a response etc.

You would need to set up a mailbox for it to use, on your server or some other mail server. Once you've done that, replace the following variables in the code with yours:

ASSISTANT_EMAIL - email address of your assistant

ASSISTANT_EMAIL_PASSWORD - email password

ASSISTANT_IMAP_SERVER - incoming mail IMAP server

ASSISTANT_SMTP_SERVER - outgoing mail SMTP server

You may also need to change the IMAP and the SMTP ports in the code (lines 19 and 23) to match yours.

Currently the model uses GPT-3.5-TURBO from OpenAI. You'll need an OpenAI API key for it to work. You'd place it in an OPENAI_API_KEY environment variable. 

If you have access to GPT-4, you can change line 103 accordingly for a higher quality assistant experience. Watch out for your API fees though. I also strongly suggest not publishing your assistant email broadly once you set it up and keeping it confidential to yourself and/or trusted parties only - anyone can query your assistant with that knowledge.

Finally, you'll need to set up a cron job and point it to the web address where you set up your script to run the code every few minutes. If you don't have a server you can run cron jobs on, you could use a service like https://cron-job.org/en/


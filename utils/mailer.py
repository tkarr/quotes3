import tornado.template
import config
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send(from_address, from_name, recipients, subject, txt_body, html_body):
    '''
    send an email

    subject is loaded from a dictionary depending based off of
    the template used

    the email template path is set in config

    two templates are loaded. an html and a txt

    '''

    #loader = tornado.template.Loader(config.EMAIL_TEMPLATE_PATH)
    #html = loader.load(
    #    "{0}.html".format(template)).generate(data=data).decode("utf-8")
    #text = loader.load(
    #    "{0}.txt".format(template)).generate(data=data).decode("utf-8")
    recipients.append(from_address)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = "{0} <{1}>".format(from_name,
                                     from_address)
    msg['To'] = ', '.join(recipients)

    part1 = MIMEText(txt_body.decode("utf-8"), 'plain')
    part2 = MIMEText(html_body.decode("utf-8"), 'html')

    msg.attach(part1)
    msg.attach(part2)

    with smtplib.SMTP('10.1.1.3', 25) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(config.MAIL_USER, config.MAIL_PASSWORD)
        smtp.sendmail(from_address, recipients, msg.as_string())

if __name__ == "__main__":
    send("admin@awsh.org", "account_activation", {"activation_id": "123454"})

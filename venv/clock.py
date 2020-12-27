# timed email
import datetime
import os
from flask import render_template
from apscheduler.schedulers.blocking import BlockingScheduler


sched = BlockingScheduler()

@sched.scheduled_job('interval', seconds=30)
def timed_job():
    time = datetime.datetime.utcnow()
    for line in open('project/todos.csv', 'r'):
        email_date = line.split(',')[1][1:].split(' ')[0]
        if email_date == str(time).split(' ')[0]:
            email_time= line.split(',')[1][1:].split(' ')[1][0:5]
            if email_time == time.strftime('%H:%M'):
                for user in open('project/users.csv', 'r'):
                    if line.split(',')[0] == user.split(',')[0][1:]:
                        user_email = user.split(',')[1]
                        print(user_email)
                import smtplib
                gmailaddress = os.getenv('EMAIL')
                gmailpassword = os.getenv('EMAIL_PASSWORD')
                mailto = user_email
                subject = 'Todo Reminder'
                msg = render_template('email.html', todo=todo)
                message = f"Subject: {subject}\n\n{msg}"
                mailServer = smtplib.SMTP('smtp.gmail.com', 587)
                mailServer.starttls()
                mailServer.login(gmailaddress, gmailpassword)
                mailServer.sendmail(gmailaddress, mailto, message)
                mailServer.quit()

timed_job()
sched.start()
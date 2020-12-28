# timed email
import datetime
import os
import sys
from flask import render_template
from apscheduler.schedulers.blocking import BlockingScheduler


sched = BlockingScheduler()

@sched.scheduled_job('interval', seconds=2)
def timed_job():
    time = datetime.datetime.now()
    todo_file = open('project/todos.csv', 'r')
    for line in todo_file:
        sys.stdout.write(line)
        email_date = line.split(',')[1][1:].split(' ')[0]
        sys.stdout.write(email_date)
        if email_date == str(time).split(' ')[0]:
            email_time= line.split(',')[1][1:].split(' ')[1][0:5]
            sys.stdout.write(email_time)
            sys.stdout.write(time.strftime('%H:%M'))
            if email_time == time.strftime('%H:%M'):
                user_file = open('project/users.csv', 'r')
                for user in user_file:
                    sys.stdout.write(line.split(',')[0])
                    sys.stdout.write(user.split(',')[0])
                    if line.split(',')[0] == user.split(',')[0]:
                        user_email = user.split(',')[1][1:]
                        sys.stdout.write(user_email)
                        import smtplib
                        gmailaddress = os.getenv('EMAIL')
                        gmailpassword = os.getenv('EMAIL_PASSWORD')
                        mailto = user_email
                        subject = 'Todo Reminder'
                        msg = f"You have told us to remind us of your todo, {line.split(',')[2]}"
                        message = f"Subject: {subject}\n\n{msg}"
                        mailServer = smtplib.SMTP('smtp.gmail.com', 587)
                        mailServer.starttls()
                        mailServer.login(gmailaddress, gmailpassword)
                        mailServer.sendmail(gmailaddress, mailto, message)
                        mailServer.quit()
    sys.stdout.flush()


timed_job()
sched.start()

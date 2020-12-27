# timed email
import datetime
import os
from apscheduler.schedulers.blocking import BlockingScheduler



from project.routes import User, Todo, todo_arr, user_arr


sched = BlockingScheduler()

@sched.scheduled_job('interval', seconds=30)
def timed_job():
    time = datetime.datetime.utcnow()
    for todo in todo_arr:
        if todo.email_date.strftime('%H:%M') == time.strftime('%H:%M'):
            for user in user_arr:
                if todo.person_id == user[0]:
                    user_email = user[1]
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


sched.start()
# timed email
import datetime
import os
from apscheduler.schedulers.blocking import BlockingScheduler



from project.routes import db, User, Todo
email_time_list = db.session.query(Todo).filter_by(email_me=True).order_by(Todo.email_date.desc()).all()


sched = BlockingScheduler()

@sched.scheduled_job('interval', seconds=30)
def timed_job():
    time = datetime.datetime.utcnow()
    for todo in email_time_list:
        if todo.email_date.strftime('%H:%M') == time.strftime('%H:%M'):
            import smtplib
            gmailaddress = os.getenv('EMAIL')
            gmailpassword = os.getenv('EMAIL_PASSWORD')
            mailto = db.session.query(User).filter_by(id=todo.person_id).all()[0].email
            subject = 'Todo Reminder'
            msg = render_template('email.html', todo=todo)
            message = f"Subject: {subject}\n\n{msg}"
            mailServer = smtplib.SMTP('smtp.gmail.com', 587)
            mailServer.starttls()
            mailServer.login(gmailaddress, gmailpassword)
            mailServer.sendmail(gmailaddress, mailto, message)
            mailServer.quit()


sched.start()
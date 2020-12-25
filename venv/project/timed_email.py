import time
import datetime


'''todo_list = Todo.query.filter_by(email_me=True).order_by(Todo.email_date.desc()).all()
print(todo_list)'''


'''while True:
    unix = int(time.time())
    time1 = str(datetime.datetime.fromtimestamp(unix).strftime('%I:%M:%S:%p'))
    print(time1)
    if time1 == '08:34:30:PM':
        import smtplib
        gmailaddress = 'todos.reminder.emailer@gmail.com'
        gmailpassword = '{3HM(a7e`+)3JJ"]/e/6ZME'
        mailto = 'judahtrem11@gmail.com'
        subject = 'Success'
        msg = 'Was it ok'
        message = f"Subject: {subject}\n\n{msg}"
        mailServer = smtplib.SMTP('smtp.gmail.com', 587)
        mailServer.starttls()
        mailServer.login(gmailaddress, gmailpassword)
        mailServer.sendmail(gmailaddress, mailto, message)
        mailServer.quit()
        exit(0)
    time.sleep(0.5)
    print('waiting...')'''
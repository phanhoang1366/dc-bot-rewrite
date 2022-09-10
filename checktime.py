import datetime

def check_past(time):
    now = datetime.datetime.now().timestamp()
    return (time - now < 0)
    
def check_too_late(time):
    now = datetime.datetime.now().timestamp()
    return (time - now < -300)
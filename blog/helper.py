from flask import render_template

def template(templatefile):
    def decorated(f):
        return lambda **kwargs: render_template(templatefile, **f(**kwargs))
    return decorated



def humanizeTime(timestamp = None):
    """
    Returns a humanized string representing time difference
    between now() and the input timestamp.
    
    The output rounds up to days, hours, minutes, or seconds.
    4 days 5 hours returns '4 days'
    0 days 4 hours 3 minutes returns '4 hours', etc...
    """
    import datetime
   
    timeDiff = datetime.datetime.now() - timestamp
    print timeDiff
    days = timeDiff.days
    hours = timeDiff.seconds / 3600
    minutes = timeDiff.seconds % 3600 / 60
    seconds = timeDiff.seconds % 3600 % 60
    
    str = ""
    tStr = ""
    if days > 0:
        if days == 1:   
            tStr = "day"
        else: 
            tStr = "days"
        str = str + "%s %s" %(days, tStr)
        return str
    elif hours > 0:
        if hours == 1:  
            tStr = "hour"
        else:
            tStr = "hours"
        str = str + "%s %s" %(hours, tStr)
        return str
    elif minutes > 0:
        if minutes == 1:
            tStr = "min"
        else:
            tStr = "mins"           
        str = str + "%s %s" %(minutes, tStr)
        return str
    elif seconds > 0:
        if seconds == 1:
            tStr = "sec"
        else:
            tStr = "secs"
        str = str + "%s %s" %(seconds, tStr)
        return str
    else:
        return 'just now'

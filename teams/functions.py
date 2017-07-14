from datetime import date, timedelta
#from dateutil.relativedelta import relativedelta

from teams.models import Week

def date_range(start_date, end_date):
    """
    Yields each date in a week.
    """
    end_date += timedelta(days=1)
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def check_current():
    """
    Finds the current week if one exists and sets the current flag to True.
    All others are set to False.
    """
    week_set = Week.objects.all()

    if week_set.exists():
        for week in week_set.iterator():
            flag = False
            for day in date_range(week.monday, week.sunday):
                if day == date.today():
                    week.current = True
                    week.save()
                    flag = True

            # Set current flag to false if week is not current
            if not flag:
                week.current = False
                week.save()

        return True
    else:
        return False

# use relativedelta
def get_monday(n=None):
    """
    Returns the requested Monday.
    """
    day = date.today()

    # previous Monday
    if n is 0:
        while day.weekday() is not 0:
            day -= timedelta(days=1)
        return day - timedelta(days=7)

    # next Monday
    elif n is 1:
        while True:
            day += timedelta(days=1)
            if day.weekday() is 0:
                return day

    # this past Monday
    else:
        while day.weekday() is not 0:
            day -= timedelta(days=1)
        return day

from datetime import date, timedelta
#from dateutil.relativedelta import relativedelta

from teams.models import Week

def date_range(start_date, end_date):
    end_date += timedelta(days=1)
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def check_current():
    week_set = Week.objects.all()

    if week_set.exists():
        for week in week_set.iterator():
            flag = False
            for day in date_range(week.monday, week.sunday):
                if day == date.today():
                    week.current = True
                    week.save()
                    flag = True

            if not flag:
                week.current = False
                week.save()
            else:
                continue

        return True
    else:
        return False

# use relativedelta
def get_monday(n=None):
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

    # this Monday
    else:
        while day.weekday() is not 0:
            day -= timedelta(days=1)
        return day

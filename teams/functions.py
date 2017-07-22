from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from teams.models import Week, Practice

def date_range(start_date, end_date):
    """
    Yields each date in a week.
    """
    end_date += timedelta(days=1)
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def check_present():
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
                    week.present = True
                    week.save()
                    flag = True

            # Set current flag to false if week is not current
            if not flag:
                week.present = False
                week.save()

        return True
    else:
        return False

def get_monday(week=None, n=None):
    """
    Returns the requested Monday.
    """
    day = week.monday if week else date.today()

    # previous Monday
    if n is 0:
        while day.weekday() is not 0:
            day -= relativedelta(days=1)
        return day - relativedelta(days=7)

    # next Monday
    elif n is 1:
        while True:
            day += relativedelta(days=1)
            if day.weekday() is 0:
                return day

    # this past Monday
    else:
        while day.weekday() is not 0:
            day -= relativedelta(days=1)
        return day

def clean_weekday(team, practice):
    """
    Delete any other practices created on the same weekday for given team/week.
    Currently there should never be more than one practice per day
    """
    if Practice.objects.filter(team=team).filter(
        week_id=practice.week_id).filter(
        weekday=practice.weekday).exclude(pk=practice.id):
        practice_list = Practice.objects.filter(team=team).filter(
            week_id=practice.week_id).filter(
            weekday=practice.weekday).exclude(pk=practice.id)
        for p in practice_list:
            p.delete()

def get_or_create_weeks(w_id):
    """
    Gets or creates the previous, current, and next weeks to be used on the
    schedule.
    """
    weeks = {
        'current': None,
        'previous': 0,
        'next': 1,
    }

    # loop through current, next, and previous weeks
    for key in sorted(weeks):
        flag = False

        try:
            # try database queries
            if int(w_id) is 0 and 'current' in key:
                # w_id = 0 if requesting the present week
                flag = True
                check_present() # check weeks for present
                weeks[key] = Week.objects.get(present=True)
            elif int(w_id) is not 0 and 'current' in key:
                # get week with id w_id as 'current'
                weeks[key] = Week.objects.get(id=w_id)
            else:
                # get next and previous weeks (for next/previous buttons)
                weeks[key] = weeks['current'].get_week(weeks[key])

        except Week.DoesNotExist:
            # else create week
            if not flag: # return date of necessary Monday
                monday = get_monday(weeks['current'], weeks[key])
            else:
                monday = get_monday(weeks[key])
            weeks[key] = Week.objects.create(monday=monday, present=flag)
            weeks[key].populate() # populate dates for rest of week

    return weeks

def get_practices_and_dates(team, weeks):
    """
    Returns two lists: one of practice, weekday tuples; and one of weekday, date
    tuples.
    """
    practices = []
    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday' ,'sunday']
    for day in weekdays:
        # create list of practices
        try:
            practices.append(Practice.objects.filter(team=team).filter(
                week_id=weeks['current']).order_by('order').get(weekday=day))
        except Practice.DoesNotExist:
            practices.append(None)

    practices = zip(practices, weekdays) # add weekdays
    dates = Week.objects.filter(pk=weeks['current'].id).values(
        'monday',
        'tuesday',
        'wednesday',
        'thursday',
        'friday',
        'saturday',
        'sunday',
    )[0] # unpack dates from current week
    dates = zip(dates.keys(), dates.values()) # zip into tuples

    return practices, dates

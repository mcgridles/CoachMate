from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from teams.models import *

def check_present():
    """
    Finds the current week if one exists and sets the current flag to True.
    All others are set to False.
    """
    week_set = Week.objects.all()

    if week_set.exists():
        for week in week_set.iterator():
            flag = False
            for day in week.date_range():
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
    practice_list = Practice.objects.filter(team=team).filter(
        week_id=practice.week_id).filter(
        weekday=practice.weekday).exclude(pk=practice.id)
    if practice_list.exists():
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


def get_zipped_set(setInstance):
    """
    Returns a list of tuples that represents a set in the
    (Swimmer, (Rep, Interval)) format
    """
    swimmers = []
    swimmer_reps = []
    for swimmer in setInstance.swimmers.all():
        swimmers.append(swimmer)
        reps = []
        intervals = []
        for rep in setInstance.rep_set.all():
            # get interval object
            try:
                interval = Interval.objects.filter(rep=rep).get(swimmer=swimmer)
                if interval.time == timedelta(seconds=0):
                    interval = None
            except Interval.DoesNotExist:
                interval = None

            reps.append(rep)
            intervals.append(interval)
        swimmer_reps.append(zip(reps, intervals)) # list of (Rep, Interval) tuples

    return zip(swimmers, swimmer_reps) # list of (Swimmer, (Rep, Interval)) tuples)


def get_practices_and_dates(team, weeks):
    """
    Returns two lists: one of practice, weekday tuples; and one of weekday, date
    tuples.
    """
    practices = []
    practice_sets = []
    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday' ,'sunday']
    for day in weekdays:
        # create list of practices
        try:
            sets = []
            swimmers = []
            practice = Practice.objects.filter(team=team).filter(
                week_id=weeks['current']).get(weekday=day)
            for s in practice.set_set.all():
                sets.append(s) # Set object
                # list of (Swimmer, (Rep, Interval)) tuples
                swimmers.append(get_zipped_set(s))

            # list of (Set, (Swimmer, (Rep, Interval))) tuples
            practice_sets.append(zip(sets, swimmers))
            practices.append(practice)
        except Practice.DoesNotExist:
            practice_sets.append((None, (None, (None, None))))
            practices.append(None)

    # list of (Practice, (Set, (Swimmer, (Rep, Interval)))) tuples
    practices = zip(practices, practice_sets)
    # list of ((Practice, (Set, (Swimmer, (Rep, Interval)))), weekday) tuples
    practices = zip(practices, weekdays)
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


def calculate_intervals(setInstance, training_model):
    """
    Calculates intervals for each rep for each swimmer.
    """
    try:
        multiplier = float(training_model.trainingmultiplier_set.get(focus=setInstance.focus).multiplier)
    except (AttributeError, TrainingMultiplier.DoesNotExist):
        multiplier = None

    reps = []
    swimmers = []
    intervals = []

    if multiplier:
        for rep in setInstance.rep_set.all():
            num_50 = rep.distance / 50 # number of 50s for the distance
            for swimmer in setInstance.swimmers.all():
                base = swimmer.get_base(setInstance.pace, rep.stroke) # get base
                if multiplier and base:
                    # add multiplier to base
                    time = timedelta(seconds=((1 + multiplier) * base.total_seconds()))
                    # multiply base by the number of 50s
                    time = timedelta(seconds=(num_50 * time.total_seconds()))

                    if setInstance.pace == 'train':
                        # training intervals should end in :00 or :05
                        time = timedelta(seconds=int(time.total_seconds()))
                        while int(time.total_seconds() % 5):
                            time += timedelta(seconds=1)
                    else:
                        time = timedelta(seconds=int(time.total_seconds()))

                else:
                    # time is 0 if no multiplier is set
                    # essentially a flag
                    time = timedelta(seconds=0)

                # create interval object
                intervals = Interval.objects.filter(rep=rep).filter(swimmer=swimmer)
                for interval in intervals:
                    interval.delete()
                interval = Interval.objects.create(swimmer=swimmer, rep=rep, time=time)

        return True

    else:
        return False


def get_swimmer_records(swimmer):
    """
    Returns the fastest time in each event for the given swimmer or None if there
    is no time for the event.
    """
    records = []
    for event in EVENT_CHOICE:
        if 'base' in event[0]:
            continue
        records.append((event[1], swimmer.get_best_time(event[0])))

    return records


def get_team_records(team):
    """
    Returns the fastest time in each event for the given team for men and women
    or None if there is no time for the event.
    """
    records = []
    for event in EVENT_CHOICE:
        if 'base' in event[0]:
            continue
        records.append(team.get_record(event))

    return records

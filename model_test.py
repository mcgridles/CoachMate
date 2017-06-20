# Structure is pretty good, may need more info
class Swimmer(object):
    # more info might be needed
    info = {
        'first': '',
        'last': '',
        'gender': '',
        'age': 0,
        'team': '', # ?
    }

    # list of best times, sorted so best is first (ascending)
    # can be used for stat tracking or best time
    times {
        '50 Free': [],
        '100 Free': [],
        '200 Free': [],
        '500 Free': [],
        '1000 Free': [],
        '50 Fly': [],
        '100 Fly': [],
        '200 Fly': [],
        '50 Back': [],
        '100 Back': [],
        '200 Back': [],
        '50 Breast': [],
        '100 Breast': [],
        '200 Breast': [],
    }


# Is there a better name for this?
class Rep(object):
    Reps = 0
    Distance = 0
    Stroke = ''
    Comments = ''


# I have no idea what the best way to incorporate distances, reps, and more
# importantly special instructions
# May be unnecessary
class Set(object):
    ID = 000
    Repeats = 0
    Reps = []


# Maybe eliminate and just put list of sets in Week class
class Practice(object):
    """
    Practices need to be able to be modified by skill level.
    Slower swimmers should have fewer reps and slower intervals -> intervals can
    be calculated based on best time in target event. Maybe use best times to
    create spread of skill level and different percentiles do different # of reps.
    Different swimmers should also be able to do different sets i.e. sprint, kick,
    distance, etc sets.
    """

    # Could do this instead of set class. Description used to know what set is what,
    # something will be needed to identify sets
    # List of set objects could also be used
    sets = [
        {'Repeats': 0, 'Reps': [], 'Description': ''},
    ]


# Practices need to be able to be planned an entire week at a time
class Week(object):
    # day structure - repeat for entire week
    # could also store in dict of dicts
    Monday = {
        'Practice': None,
        'Swimmers': {} # name: attendance status
        #'Attendance': [],
    }

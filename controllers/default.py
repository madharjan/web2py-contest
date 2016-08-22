from datetime import datetime

def check_ticket_pin(form):

    result = db(db.vote.ticket_no == form.vars.ticket_no).select(db.vote.ticket_no.count().with_alias('count')).first();
    if result['count'] > 0 :
        # voted already
        form.errors.ticket_no = 'You have already voted'
    else:
        result = db(db.ticket.ticket_no == form.vars.ticket_no).select(db.ticket.ticket_no.count().with_alias('count')).first();
        if result['count'] > 0 :
            # valid ticket_no
            result = db((db.ticket.ticket_no == form.vars.ticket_no) &
                        (db.ticket.ticket_pin == form.vars.ticket_pin)).select(db.ticket.ticket_no.count().with_alias('count')).first();

            if result['count'] == 0 :
               # invalid ticket_no & ticket_pin
               form.errors.ticket_pin = 'Invalid PIN'
        else:
            # invalid ticket_no
            form.errors.ticket_no = 'Invalid Ticket No'
    return

def index():

    registration = dict()
    voting = dict()
    lucky_draw = dict()

    result = db().select(db.settings.ALL)
    for row in result:
        if row.name == "registration":
            registration = dict(start = row.start_time, end = row.end_time)
        elif row.name == "voting":
            voting = dict(start = row.start_time, end = row.end_time)
        elif row.name == "lucky_draw":
            lucky_draw = dict(start = row.start_time, end = row.end_time)


    return dict(registration = registration, voting = voting, lucky_draw = lucky_draw)

def vote():

    contestants = db().select(db.contestant.code.count().with_alias('count')).first()

    form=SQLFORM(db.vote)
    form.vars.voted_datetime = datetime.today().strftime('%Y-%m-%d %I:%M %p:%S')

    voting = db(db.settings.name == 'voting').select(db.settings.start_time, db.settings.end_time).first();
    now = datetime.now()
    if  now < voting.start_time:
        response.flash = "Voting has not started yet, it will start at " + datetime.strftime(voting.start_time, '%d %b %Y, %I:%M %p')
    elif now > voting.end_time:
        response.flash = "Voting has ended already, it ended at " + datetime.strftime(voting.end_time, '%d %b %Y, %I:%M %p')
    elif form.accepts(request.vars, session, onvalidation=check_ticket_pin):
        response.flash = 'Thank you for voting'
    elif form.errors:
        if form.errors.contestant_id : form.errors.contestant_id = 'Select a value'
        response.flash = 'Check form error'

    return dict(form = form, interval = contestants.count * 3000 + 3000)


def result():

    votes = db().select(db.vote.contestant_id.count().with_alias('total')).first()
    result = db().select(db.contestant.id,
                         db.contestant.code,
                         db.contestant.name,
                         db.contestant.photo,
                         db.vote.contestant_id.count().with_alias('count'),
                         left = db.vote.on(db.contestant.id == db.vote.contestant_id),
                         groupby = db.contestant.id,
                         orderby =~ db.vote.contestant_id.count())

    contestants = list()
    for row in result:
        contestant = dict(id = row.contestant.id,
                        code = row.contestant.code,
                        name = row.contestant.name,
                       photo = row.contestant.photo,
                       votes = row.count)
        contestants.append(contestant)

    return dict(contestants = contestants, total = votes.total, interval = len(contestants) * 3000 + 3000)

def download():

    return response.download(request, db)

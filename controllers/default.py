from datetime import datetime

def index():

    form=SQLFORM(db.vote)
    form.vars.voted_datetime = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    if form.process().accepted:
       response.flash = 'vote accepted'
    elif form.errors:
       response.flash = 'form has errors'
    else:
       response.flash = 'please fill out the form'

    return dict(form = form)


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

    return dict(contestants = contestants, total = votes.total)


def download():

    return response.download(request, db)

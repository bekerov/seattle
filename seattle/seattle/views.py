from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError
from sqlalchemy import func


from .models import (
    DBSession,
    MyModel,
    )

import datetime

class PST(datetime.tzinfo):
    """Class defining correct timezone, used in epoch_time."""
    def utcoffset(self, dt):
        return datetime.timedelta(hours=-8)

    def dst(self, dt):
        return datetime.timedelta(0)

def epoch_time(dt):
    """Method to convert datetime object into epoch time in days."""
    epoch = datetime.datetime.fromtimestamp(0, PST())
    # import pdb; pdb.set_trace()
    delta = dt - epoch
    return delta.total_seconds()/60/60/24

@view_config(route_name='home', renderer='templates/test.jinja2')
def my_view(request):
    try:
        one = DBSession.query(MyModel).filter(MyModel.gid == 378).first()
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    return {'one': one, 'project': 'seattle'}

@view_config(route_name='one_hundred', renderer='json')
def one_hundred(request):
    try:
        output = DBSession.query(MyModel).filter(func.ST_Point_Inside_Circle(MyModel.the_geom, -122.336072, 47.623636, 0.001))
        # print 'query: {}\ncount: {}'.format(output, output.count())


    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    list_ = []
    for x in output:
        """Convert datetime into epoch_time."""
        x.__dict__['date_time'] = epoch_time(x.__dict__['date_time'])
        del x.__dict__['_sa_instance_state']
        list_.append(x.__dict__)

    return {'output': list_}

conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_seattle_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""


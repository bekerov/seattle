from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    func
    )
import sqlalchemy as sa

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension
import time

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Incidents_Model(Base):
    __tablename__ = 'incidents'
    gid = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    units = sa.Column(sa.UnicodeText, nullable=False)
    date_time = sa.Column(sa.DateTime, nullable=False)
    incident_type = sa.Column(sa.UnicodeText, nullable=False)
    address = sa.Column(sa.UnicodeText, nullable=False)
    incident_number = sa.Column(sa.UnicodeText, nullable=False)
    latitude = sa.Column(sa.UnicodeText, nullable=False)
    longitude = sa.Column(sa.UnicodeText, nullable=False)
    major_category = sa.Column(sa.UnicodeText, nullable=False)
    minor_category = sa.Column(sa.UnicodeText, nullable=False)
    the_geom = sa.Column(sa.UnicodeText, nullable=False)

    @classmethod
    def by_gid(cls, gid):
        return DBSession.query(cls).filter(cls.gid == gid).one()

    @classmethod
    def by_incident_type(cls, incident_type):
        return (DBSession.query(cls).filter(cls.incident_type == incident_type)
                .all())

    @classmethod
    def circle_radius(cls, lat, lon, radius):
        return (DBSession.query(cls)
                .filter(func.ST_Point_Inside_Circle(cls.the_geom,
                                                    lon, lat, radius)).all()
                )

    @classmethod
    def random_circle(cls, lat, lon, radius, limit):
        """Outputs random entries from a given radius, with limited number."""
        return (DBSession.query(cls)
                .order_by(func.random())
                .filter(func.ST_Point_Inside_Circle(cls.the_geom, lon, lat,
                                                    radius)).limit(limit)
                )

    @classmethod
    def cat_circle(cls, lat, lon, major_cat, radius=0.003, limit=1000):
        """Outputs list of incidents filtered by Major Category"""
        return (DBSession.query(cls)
                .order_by(func.random())
                .filter(func.ST_Point_Inside_Circle(cls.the_geom, lon, lat,
                                                    radius),
                        cls.major_category == major_cat)
                .limit(limit)
                )

    @classmethod
    def percentage(cls, list_of_times):
        """Given a list of times in epoch time, return the percentage increase over the last year."""
        # current epoch time in days
        # current_epoch_time = time.time()/60/60/24
        one_year_ago_epoch = list_of_times[-1]-365
        length_list = len(list_of_times)
        incidents_prior = 0
        for time in list_of_times:
            if time < one_year_ago_epoch:
                incidents_prior += 1
            if time > one_year_ago_epoch:
                break

        incidents_last_year = length_list-incidents_prior
        years_prior = (one_year_ago_epoch-list_of_times[0])/365
        incidents_per_year_prior = incidents_prior/years_prior
        incidents_per_year_last_year = incidents_last_year
        percent = 100*(incidents_per_year_last_year-incidents_per_year_prior)/incidents_per_year_prior
        return round(percent, 2)


    def json(self):
        return {'gid': self.gid,
                'units': self.units,
                'date_time': self.date_time,
                'incident_type': self.incident_type,
                'address': self.address,
                'incident_number': self.incident_number,
                'latitude': self.latitude,
                'longitude': self.longitude,
                'the_geom': self.the_geom}



# I don't know what this line is for:
Index('my_index', Incidents_Model.gid, unique=True, mysql_length=255)

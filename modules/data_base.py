"""
-- Таблица: regions
CREATE TABLE regions (id INTEGER PRIMARY KEY, Name VARCHAR (32) UNIQUE);

-- Таблица: skills
CREATE TABLE skills (id INTEGER PRIMARY KEY AUTOINCREMENT, Name VARCHAR (32) UNIQUE);

-- Таблица: vacancies
CREATE TABLE vacancies (id INTEGER PRIMARY KEY AUTOINCREMENT, Name VARCHAR (32) UNIQUE);

-- Таблица: requests
CREATE TABLE requests (id INTEGER PRIMARY KEY AUTOINCREMENT, Data VARCHAR (9), idRegion REFERENCES regions (id),
                       idVacancy REFERENCES vacancies (id), Found INTEGER);
-- Индекс: request
CREATE INDEX request ON request_skill (idRequest);

-- Таблица: request_skill
CREATE TABLE request_skill (idRequest REFERENCES requests (id), idSkill REFERENCES skills (id),
                            Count INTEGER, Percent REAL);
"""

from sqlalchemy import Column, Integer, String, REAL, create_engine, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


Base = declarative_base()


class Regions(Base):
    __tablename__ = 'regions'
    id = Column(Integer, primary_key=True)
    Name = Column(String, unique=True)

    # пока не будем хранить внутренний номер региона из hh.ru

    def __init__(self, name):
        self.Name = name

    def __str__(self):
        return self.Name


class Skills(Base):
    __tablename__ = 'skills'
    id = Column(Integer, primary_key=True)
    Name = Column(String, unique=True)

    def __init__(self, name):
        self.Name = name

    def __str__(self):
        return self.Name


class Vacancies(Base):
    __tablename__ = 'vacancies'
    id = Column(Integer, primary_key=True)
    Name = Column(String, unique=True)

    def __init__(self, name):
        self.Name = name

    def __str__(self):
        return self.Name


class Requests(Base):
    __tablename__ = 'requests'
    id = Column(Integer, primary_key=True)
    Data = Column(String)
    idRegion = Column(Integer, ForeignKey('regions.id'))
    idVacancy = Column(Integer, ForeignKey('vacancies.id'))
    Found = Column(Integer)

    region = relationship('Regions', backref='requests')
    vacancy = relationship('Vacancies', backref='requests')

    def __init__(self, data, id_region, id_vacancy, found):
        self.Data = data
        self.idRegion = id_region
        self.idVacancy = id_vacancy
        self.Fond = found

    def __str__(self):
        return self.id


class RequestSkill(Base):
    __tablename__ = 'request_skill'
    id = Column(Integer, primary_key=True)
    idRequest = Column(Integer, ForeignKey('requests.id'), index=True)
    idSkill = Column(Integer, ForeignKey('skills.id'))
    Count = Column(Integer)
    Percent = Column(REAL)

    def __init__(self, id_request, id_skill, count, percent):
        self.idRequest = id_request
        self.idSkill = id_skill
        self.Count = count
        self.Percent = percent

#https://stackoverflow.com/questions/2546207/does-sqlalchemy-have-an-equivalent-of-djangos-get-or-create

def add_records(info):
    engine = create_engine('sqlite:///modules\hhparser.db', echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    session.add(Regions(info['region']))
    id_region = session.query(Regions.id).filter(Regions.Name == info['region']).all()[0][0]
    session.add(Vacancies(info['vacancy']))
    id_vacancy = session.query(Vacancies.id).filter(Vacancies.Name == info['vacancy']).all()[0][0]
    session.add(Requests(info['data'], id_region, id_vacancy, info['found']))
    id_request = session.query(Requests.id).filter(Requests.Data == info['data'] and Requests.idRegion == id_region and
                                                   Requests.idVacancy == id_vacancy and
                                                   Requests.Found == info['found']).all()[0][0]

    for skill in info['requirement']:
        # скилы
        session.add(Skills(skill['name']))
        id_skill = session.query(Skills.id).filter(Skills.Name == skill['name']).all()[0][0]
        # реквест-скилы
        session.add(RequestSkill(id_request, id_skill, skill['count'], skill['percent']))

    session.commit()
    session.close()
    return


if __name__ == '__main__':
    engine = create_engine('sqlite:///hhparser.db', echo=True)
    # Создание таблицы
    Base.metadata.create_all(engine)

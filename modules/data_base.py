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
    idRegion = Column(Integer)
    idVacancy = Column(Integer)
    Found = Column(Integer)

    def __init__(self, data, id_region, id_vacancy, found):
        self.Data = data
        self.idRegion = id_region
        self.idVacancy = id_vacancy
        self.Found = found

    def __str__(self):
        return self.id


class RequestSkill(Base):
    __tablename__ = 'request_skill'
    id = Column(Integer, primary_key=True)
    idRequest = Column(Integer)
    idSkill = Column(Integer)
    Count = Column(Integer)
    Percent = Column(REAL)

    def __init__(self, id_request, id_skill, count, percent):
        self.idRequest = id_request
        self.idSkill = id_skill
        self.Count = count
        self.Percent = percent


def get_or_create(session, model, info):
    exist = session.query(model.id).filter(model.Name == info).first()
    if not exist:
        session.add(model(info))
    return session.query(model.id).filter(model.Name == info).first()[0]


def add_records(info):
    engine = create_engine('sqlite:///modules\hhparser.db', echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    id_region = get_or_create(session, Regions, info['region'])
    id_vacancy = get_or_create(session, Vacancies, info['vacancy'])

    exist = session.query(Requests.id).filter(Requests.Data == info['data'],
                                              Requests.idRegion == id_region,
                                              Requests.idVacancy == id_vacancy,
                                              Requests.Found == info['found']).first()
    if not exist:
        session.add(Requests(info['data'], id_region, id_vacancy, info['found']))

    id_request = session.query(Requests.id).filter(Requests.Data == info['data'],
                                                   Requests.idRegion == id_region,
                                                   Requests.idVacancy == id_vacancy,
                                                   Requests.Found == info['found']).first()[0]

    for skill in info['requirement']:
        # скилы
        id_skill = get_or_create(session, Skills, skill['name'])
        # реквест-скилы
        session.add(RequestSkill(id_request, id_skill, skill['count'], skill['percent']))

    session.commit()
    session.close()
    return


if __name__ == '__main__':
    # Создание таблицы
    engine = create_engine('sqlite:///hhparser.db', echo=True)
    Base.metadata.create_all(engine)

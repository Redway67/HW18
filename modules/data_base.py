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
from sqlalchemy.orm import sessionmaker, relationship, backref

DB_ENGINE = 'sqlite:///modules\hhparser.db'
Base = declarative_base()

RequestSkill = Table('RequestSkill',
                     Column('idRequest', Integer, ForeignKey('requests.id')),
                     Column('idVacancy', Integer, ForeignKey('vacancies.id')),
                     Column('Count', Integer),
                     Column('Percent', REAL)
                     )


class Regions(Base):
    __tablename__ = 'regions'
    id = Column(Integer, primary_key=True)
    Name = Column(String, unique=True)
    request = relationship('Requests', backref='region')

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
    request = relationship('Requests', backref='vacancy')

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
    Requirement = relationship('Skills', secondary=RequestSkill, backref=backref('requirements', lazy='dynamic'))

    def __init__(self, data, id_region, id_vacancy, found):
        self.Data = data
        self.idRegion = id_region
        self.idVacancy = id_vacancy
        self.Found = found

    def __str__(self):
        return self.id


# class RequestSkill(Base):
#     __tablename__ = 'request_skill'
#     id = Column(Integer, primary_key=True)
#     idRequest = Column(Integer)
#     idSkill = Column(Integer)
#     Count = Column(Integer)
#     Percent = Column(REAL)
#
#     def __init__(self, id_request, id_skill, count, percent):
#         self.idRequest = id_request
#         self.idSkill = id_skill
#         self.Count = count
#         self.Percent = percent


def get_or_create(session, model, info):
    exist = session.query(model.id).filter(model.Name == info).first()
    if not exist:
        session.add(model(info))
    return session.query(model.id).filter(model.Name == info).first()[0]


def add_records(info):
    engine = create_engine(DB_ENGINE, echo=False)
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


def get_history():
    history_db = []
    engine = create_engine(DB_ENGINE, echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    queries = session.query(Requests).all()
    for item in queries:
        history_db.append(
            f'Регион: {item.region.Name}, Вакансия: {item.vacancy.Name}, Найдено: {item.Found},'
            f' Дата: {item.Data}, Запрос: {item.id}')
    session.close()
    return history_db


def get_request(request):
    # TODO: обработка пустого запроса
    r = request.replace(':', ',').split(',')
    id_request = r[9].split()[0]
    region = r[1].split()[0]
    vacancy = r[3].split()[0]
    found = r[5].split()[0]
    data = r[7].split()[0]

    engine = create_engine(DB_ENGINE, echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    skills = session.query(RequestSkill).filter(RequestSkill.idRequest == id_request).all()
    req = []
    for skill in skills:
        print(skill.idSkill)
        # req.append({'name': name, 'count': skill[2], 'percent': skill[3]})

    info = {'region': region, 'vacancy': vacancy, 'found': found, 'data': data, 'requirement': req}
    session.close()
    return info


if __name__ == '__main__':
    # Создание таблицы
    engine = create_engine('sqlite:///hhparser.db', echo=True)
    Base.metadata.create_all(engine)

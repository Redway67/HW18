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

engine = create_engine('sqlite:///hhparser.db', echo=True)
Base = declarative_base()

request_skill = Table('request_skill', Base.metadata,
                      Column('idRequest', Integer, ForeignKey('requests.id'), index=True),
                      Column('idSkill', Integer, ForeignKey('skills.id')),
                      Column('Count', Integer),
                      Column('Percent', REAL)
                      )


class Regions(Base):
    __tablename__ = 'regions'
    id = Column(Integer, primary_key=True)
    Name = Column(String, unique=True)

    def __str__(self):
        return self.Name


class Skills(Base):
    __tablename__ = 'skills'
    id = Column(Integer, primary_key=True)
    Name = Column(String, unique=True)

    def __str__(self):
        return self.Name


class Vacancies(Base):
    __tablename__ = 'vacancies'
    id = Column(Integer, primary_key=True)
    Name = Column(String, unique=True)

    def __str__(self):
        return self.Name


class Requests(Base):
    __tablename__ = 'requests'
    id = Column(Integer, primary_key=True)
    Data = Column(String)
    idRegion = Column(Integer)
    idVacancy = Column(Integer)
    Found = Column(Integer)

    # def __str__(self):
    #   return self.Name


if __name__ == '__main__':
    # Создание таблицы
    Base.metadata.create_all(engine)

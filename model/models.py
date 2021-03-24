from datetime import datetime
# from pydantic import BaseModel, HttpUrl
# from typing import Optional
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship

from .database import Base


class Account(Base):
    __tablename__ = "account"

    accountid = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    displayname = Column(String, index=True)
    createddate = Column(DateTime, default=datetime.utcnow)
    karma = Column(Integer, default=0)
    accounthash = Column(Integer, default=0)

    submissions = relationship("Submission", back_populates="account")
    votes = relationship("Vote", back_populates="account")

class Video(Base):
    __tablename__ = "video"

    videoid = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=False, index=True)
    title = Column(String)
    thumbnail = Column(String)
    length = Column(Float)

    submissions = relationship("Submission", back_populates="video")
    votes = relationship("Vote", back_populates="video")

class Submission(Base):
    __tablename__ = "submission"

    submissionid = Column(Integer, primary_key=True, index=True)
    videoid = Column(Integer, ForeignKey("video.videoid"))
    accountid = Column(Integer, ForeignKey("account.accountid"))
    starttime = Column(Integer)
    endtime = Column(Integer)
    requestdate = Column(DateTime, default=datetime.utcnow)
    # hasplayed = Column(Boolean, default=False)
    played_date = Column(DateTime)
    vote_total = Column(Integer, default=0)

    video = relationship("Video", back_populates="submissions")
    account = relationship("Account", back_populates="submissions")
    votes = relationship("Vote", back_populates="submission")

class Vote(Base):
    __tablename__ = "vote"
    voteid = Column(Integer, primary_key=True, index=True)
    videoid = Column(Integer, ForeignKey("video.videoid"))
    submissionid = Column(Integer, ForeignKey("submission.submissionid"))
    accountid = Column(Integer, ForeignKey("account.accountid"))
    votetype = Column(String, index=True)
    votetime = Column(DateTime, default=datetime.utcnow)
    voteval = Column(Integer)

    video = relationship("Video", back_populates="votes")
    submission = relationship("Submission", back_populates="votes")
    account = relationship("Account", back_populates="votes")

class Stupid(Base):
    __tablename__ = "stupid"
    stupidid = Column(Integer, primary_key=True, index=True)
    started_time = Column(DateTime, default=datetime.utcnow)
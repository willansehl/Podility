import datetime
from typing import List, Optional
from pydantic import BaseModel

class Account(BaseModel):
    accountid: int
    username: str
    displayname: str
    createddate: datetime.datetime
    karma: int
    accounthash: int

class Video(BaseModel):
    videoid: int
    url: str
    title: str
    thumbnail: str
    length: float

class Submission(BaseModel):
    submissionid: int
    videoid: int
    starttime: int
    endtime: int
    accountid: int
    requestdate: datetime.datetime
    # hasplayed: bool
    played_date: datetime.datetime
    vote_total: int

class Vote(BaseModel):
    voteid: int
    videoid: int
    submissionid: int
    votetype: int
    requestedby: int
    votetime: datetime.datetime
    voteval: int

class SubmissionRequest(BaseModel):
    url: str
    start: Optional[int]
    end: Optional[int]
    userid: str

class AccountCreate(BaseModel):
    username: str
    display_name: str

class Stupid(BaseModel):
    stupidid: str
    started_time: datetime.datetime
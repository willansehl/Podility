from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import DateTime, desc, func
from . import models, schemas

def get_account(db: Session, account_id: int):
    return db.query(models.Account).filter(models.Account.id == account_id).first()

def get_account_from_hash(db: Session, account_hash: int):
    print("getting account for hash: " + str(account_hash))
    return db.query(models.Account).filter(models.Account.accounthash == account_hash).first()

def create_account(db: Session, username: str, displayName: str):
    db_user = models.Account(username=username, displayname=displayName)
    db.add(db_user)
    db.commit()
    db_user.accounthash = hash(username + str(db_user.accountid))
    db.commit()
    db.refresh(db_user)
    return db_user

def create_video(db: Session, url: str, title: str, thumbnail: str, length: float):
    db_video = models.Video(url=url, title=title, thumbnail=thumbnail, length=length)
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video

def get_video(db: Session, url: str):
    return db.query(models.Video).filter(models.Video.url == url).first()

def submit_video(db: Session, channel_id: int, requestedBy: int, url: str, title: str, thumbnail: str, length: float, start: int = 0, end: int = 0):
    db_video = get_video(db, url=url)
    if not db_video: db_video = create_video(db, url=url, title=title, thumbnail=thumbnail, length=length)

    db_submission = models.Submission(videoid=db_video.videoid, accountid=requestedBy, starttime=start, endtime=end)
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission

def get_submission(db: Session, id: int):
    return db.query(models.Submission).filter(models.Submission.submissionid == id).first()

def get_submissions(db: Session, pod_name: str):
    return db.query(models.Submission).filter(models.Submission.played_date == None).all()

def mark_submission_as_played(db: Session, submissionid: int):
    submission = get_submission(db, submissionid)
    submission.played_date=datetime.now()
    db.commit()

def get_top_submission(db: Session):
    print("getting top submission")
    return db.query(models.Submission).filter(models.Submission.played_date == None).order_by(desc(models.Submission.vote_total)).first()

def get_currently_playing(db: Session):
    return db.query(models.Submission).filter(models.Submission.played_date != None).order_by(desc(models.Submission.played_date)).first()

def add_vote(db: Session, submission_id: int, account_id: int, vote_type: str, vote_val: int):
    submission = get_submission(db=db, id=submission_id)
    submission.vote_total += vote_val
    db_vote = models.Vote(submissionid=submission_id, videoid=submission.videoid, accountid=account_id, votetype=vote_type, voteval=vote_val)
    db.add(db_vote)
    db.commit()
    db.refresh(db_vote)
    return db_vote

def get_votes_for_submission(db: Session, submission_id: int, account_id: int, type: str):
    return db.query(models.Vote).filter(models.Vote.submissionid == submission_id, models.Vote.accountid == account_id, models.Vote.votetype == type).all()

def get_last_startup(db: Session):
    last = db.query(models.Stupid).order_by(desc(models.Stupid.started_time)).first()
    if last: return last.started_time
    else: return 0

def create_startup_record(db: Session):
    db_record = models.Stupid()
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record
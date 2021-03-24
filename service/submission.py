import operator
from typing import Optional
from .yt import yt
from datetime import datetime

from fastapi.responses import JSONResponse
from model.crud import *

"""
Handle user-submitted videos
"""

class SubmissionService:

    """
    Submit video to playlist of channel denoted by channel_id.
    Check video for length using youtube api.
    """
    def submitVideo(db, youtube, account_id, channel_id, url: str):
        title, thumbnail, duration = youtube.ytRequest(url)
        db_submission = submit_video(db=db, channel_id=channel_id, requestedBy=account_id, url=url, title=title, thumbnail=thumbnail, length=duration)
        SubmissionService.submissionVote(db, db_submission.submissionid, account_id, 1, 'playlist')

        # todo also send timestamp
        return JSONResponse({'status': 'ok', 'url': url, 'id': db_submission.submissionid, 'title': title, 'thumbnail': thumbnail, 'upvotes': 1, 'downvotes': 0 })

    def getPlaylist(db, pod_name):
        subs = get_submissions(db=db, pod_name=pod_name)
        playlist = [submissionToRet(s) for s in subs]
        playlist = sorted(playlist, key=lambda i: i['val'], reverse=True)
        return JSONResponse({'status': 'ok', 'playlist': playlist})

    def submissionVote(db, submission_id, account_id, val, type):
        votes = get_votes_for_submission(db, submission_id, account_id, type)
        if votes: return JSONResponse({'status': 'ok', 'result':'already_voted'})
        add_vote(db, submission_id=submission_id, account_id=account_id, vote_type=type, vote_val=val)
        return JSONResponse({'status': 'ok', 'result': 'accepted'})

    def getNextVideo(db):
        print("getting next video")
        next_submission = get_top_submission(db)
        return submissionToRet(next_submission)

    def getCurrentlyPlaying(db):
        ret = None
        current_submission = get_currently_playing(db)
        if current_submission:
            length = current_submission.video.length
            started_at = current_submission.played_date
            time_now = datetime.now()
            diff = time_now - started_at
            play_from = int(diff.total_seconds())
            if(play_from < length): ret = submissionToRet(current_submission, play_from=play_from)
        return JSONResponse({'status': 'ok', 'video': ret})

    def createPlayRecord(db, submission):
        print("marking as played")
        mark_submission_as_played(db, submission['id'])



def submissionToRet(submission, play_from = ""):
    if submission is None: return {}
    video = submission.video
    votes = submission.votes
    upvotes, downvotes = 0,0
    for vote in votes:
        if vote.voteval >= 0: 
            upvotes+=1
        else:
            downvotes += 1

    if '?v=' in video.url:
        yt_id = video.url.split('?v=')[1]
    else:
        yt_id = video.url

    return {
        "thumbnail": video.thumbnail,
        "link": video.url,
        "title": video.title,
        "id": submission.submissionid,
        "yt_id": yt_id,
        "upvotes": upvotes,
        "downvotes": downvotes,
        "val": upvotes-downvotes,
        "length": video.length,
        "play_from": play_from
        }

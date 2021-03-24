import sys
import random
import time
import asyncio
import json
from datetime import datetime
from typing import Optional, List
from fastapi import Depends, FastAPI, Request, WebSocket, WebSocketDisconnect, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from fastapi import Cookie, Depends, FastAPI, Query, WebSocket, status

from model import crud, models, schemas
from model.database import SessionLocal, engine
from model.schemas import Video, Submission, SubmissionRequest, AccountCreate
from model.chat import ChatMessage
from service.submission import SubmissionService
from service.util import MetadataService
from service.yt import yt

models.Base.metadata.create_all(bind=engine)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


manager = ConnectionManager()


print('creating app at time ', time.time())
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="template")
html = templates.TemplateResponse


@app.on_event("startup")
async def startup_event():
    db = SessionLocal()

    ###############################
    # this code is an abomination
    # "one of the dumbest hacks i've been a part of"
    ###############################
    print('starting app instance, waiting for permission')
    duration = random.random() * 10
    print(f'sleeping for {duration} seconds')
    time.sleep(duration)

    difference = (datetime.utcnow() - crud.get_last_startup(db)).total_seconds()
    first = difference > 10.0
    print(f'{difference} seconds since last startup')

    if not first:
        sys.exit()
    else:
        crud.create_startup_record(db)

    ###############################

    app.state.youtube = yt()
    print("startup called")
    asyncio.ensure_future(run_playlist(db))


@app.on_event("shutdown")
async def shutdown_event():
    pass

async def run_playlist(db):
    if hasattr(app.state, 'playlistThread') and app.state.playlistThread:
        return

    app.state.playlistThread = True
    print("Starting playlist Thread")
    while (True):
        await asyncio.sleep(2)
        # print("tick")
        next_submission = SubmissionService.getNextVideo(db)
        print("found video:",next_submission)
        if next_submission:
            print("broadcasting")
            await broadcast_data('play', next_submission)
            SubmissionService.createPlayRecord(db, next_submission)
            print(next_submission)
            print("length",next_submission['length'])
            await asyncio.sleep(next_submission['length'])
            print("done playing, looking for next video")
            # mark as played
        else:
            print("no playlist found, waiting")
            await asyncio.sleep(3)


async def broadcast_data(type, data):
    data_json = {'type': type, 'data': data}
    print(data_json)
    data_str = json.dumps(data_json)
    await manager.broadcast(data_str)

@app.get("/", response_class=HTMLResponse)
async def get_homepage(request: Request):
    return html('index.html', {'request': request})

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_account_from_hash(db, client_id)
    await manager.connect(websocket)
    await broadcast_data('join', {'username': db_user.displayname})
    try:
        while True:
            data = await websocket.receive_text()
            db_user = crud.get_account_from_hash(db, client_id)
            msg = ChatMessage(db_user.displayname, data)
            await broadcast_data('chat', msg.json())
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        db_user = crud.get_account_from_hash(db, client_id)
        msg = ChatMessage(db_user.displayname, None)
        await broadcast_data('leave', {'username': db_user.displayname})

@app.post("/createUser", response_class=JSONResponse, summary="create user")
async def create_user(request: Request, ac: AccountCreate, db: Session = Depends(get_db)):
    """
    Create a user object in the database. Respond with session token.
    """
    db_user = crud.create_account(db, username=ac.username, displayName=ac.display_name)
    print("created hash: " + str(db_user.accounthash))
    print(db_user.accounthash)
    return JSONResponse({'status': 'ok', 'userid': str(db_user.accounthash)})

@app.get("/videoSuggestion", response_class=JSONResponse, summary="submit video query")
async def search_videos(request: Request, query: str):
    """
    User-submitted video url. Respond with success/error.
    TODO: use request headers to determine user id
    TODO: validate url for video length
    TODO: channel_id parameter is ignored until after MVP
    """
    results = app.state.youtube.searchByKeyword(query)
    return JSONResponse({'status': 'ok', 'results': results})

@app.post("/submission/{channel_id}", response_class=JSONResponse, summary="submit video url")
async def submit_video(request: Request, channel_id: str, sr: SubmissionRequest, db: Session = Depends(get_db)):
    """
    User-submitted video url. Respond with success/error.
    TODO: use request headers to determine user id
    TODO: validate url for video length
    TODO: channel_id parameter is ignored until after MVP
    """
    db_user = crud.get_account_from_hash(db, sr.userid)
    await broadcast_data('pl', None)
    return SubmissionService.submitVideo(db, app.state.youtube, db_user.accountid, channel_id, sr.url)

@app.get("/submission/{submission_id}/upvote", response_class=JSONResponse, summary="upvote a video")
async def upvote_video(request: Request, submission_id: str, user_id: int = 0, db: Session = Depends(get_db)):
    """
    Upvote video. Respond with success/error.
    TODO: If user has already upvoted this video_id, deduct 1 karma from user.
    """
    db_user = crud.get_account_from_hash(db, user_id)
    await broadcast_data('pl', None)
    return SubmissionService.submissionVote(db, int(submission_id), db_user.accountid, val=1, type='playlist')

@app.get("/submission/{submission_id}/downvote", response_class=JSONResponse, summary="downvote a video")
async def downvote_video(request: Request, submission_id: str, user_id: int = 0, db: Session = Depends(get_db)):
    """
    Downvote video. Respond with success/error.
    TODO: If user has already downvoted this video_id, deduct 1 karma from user.
    """
    db_user = crud.get_account_from_hash(db, user_id)
    await broadcast_data('pl', None)
    return SubmissionService.submissionVote(db, int(submission_id), db_user.accountid, val=-1, type='playlist')

@app.get("/submission/{submission_id}/like", response_class=JSONResponse, summary="vote to skip a video")
async def like_video(request: Request, submission_id: str, user_id: int = 0, db: Session = Depends(get_db)):
    """
    Vote to skip video. Respond with success/error.
    TODO: If user has already voted to skip this video_id, deduct 1 karma from user.
    """
    db_user = crud.get_account_from_hash(db, user_id)
    return SubmissionService.submissionVote(db, int(submission_id), db_user.accountid, val=1, type='active')

@app.get("/submission/{submission_id}/skip", response_class=JSONResponse, summary="vote to skip a video")
async def skip_video(request: Request, submission_id: str, user_id: int = 0, db: Session = Depends(get_db)):
    """
    Vote to skip video. Respond with success/error.
    TODO: If user has already voted to skip this video_id, deduct 1 karma from user.
    """
    db_user = crud.get_account_from_hash(db, user_id)
    return SubmissionService.submissionVote(db, int(submission_id), db_user.accountid, val=-1, type='active')

@app.get("/playlist/{channel_id}", response_class=List[Video])
async def get_playlist(request: Request, channel_id: str, db: Session = Depends(get_db)):
    """
    Get videos in channel playlist.
    Response will be list. Zeroth item is currently playing video.
    TODO: channel_id parameter is ignored until after MVP
    """
    return SubmissionService.getPlaylist(db, channel_id)

@app.get("/getCurrentVideo", response_class=JSONResponse)
async def get_current_vodeo(request: Request, db: Session = Depends(get_db)):
    """
    Get videos in channel playlist.
    Response will be list. Zeroth item is currently playing video.
    TODO: channel_id parameter is ignored until after MVP
    """
    return SubmissionService.getCurrentlyPlaying(db)

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}

@app.get("/metadata")
def get_metadata():
    return MetadataService.get_metadata()

from apiclient.discovery import build
import isodate

class yt():
    def __init__(self):
        '''
        params:
            self.keys: (list of strings) a list of youtube api keys
            self.youtube: the youtube api to submit requests to
        '''
        key = '' # insert User API Key Here from Microsoft Academic API (temporary solution until Podility is further built out
        self.keys = ['']
        self.youtube = build('youtube', 'v3', developerKey=self.keys[0])


    def ytRequest(self, url=None):
        '''
        params
            url: (string) a user-submitted url, or youtube id
        return
            title: (string) the title of a given youtube video
            thumbnail: (string) the jpg url of a given youtube video
        '''
        if '?v=' in url:
            yt_id = url.split('?v=')[1]
        else:
            yt_id = url
        req = self.youtube.videos().list(part='snippet,contentDetails', id=yt_id, maxResults=5)
        snip = req.execute()
        title = snip['items'][0]['snippet']['title']
        thumbnail = snip['items'][0]['snippet']['thumbnails']['default']['url']
        iso_duration = snip['items'][0]['contentDetails']['duration']
        duration = isodate.parse_duration(iso_duration).total_seconds()
        return title, thumbnail, duration

    def searchByKeyword(self, keyword):
        '''
        user-submitted description/keyword
        params
            keyword: (string) a user-submitted description
        return
            titles: (list of strings) titles of youtube videos
            thumbnails: (list of strings) the jpg urls of youtube videos
        '''
        if not keyword:
            return []

        numResults = 5
        req = self.youtube.search().list(part='snippet',q=keyword,maxResults=numResults, order='viewCount')
        snip = req.execute()
        results = []
        for i in range(numResults):
            title = snip['items'][i]['snippet']['title']
            thumbnail = snip['items'][i]['snippet']['thumbnails']['default']['url']
            videoID = snip['items'][i]['id']['videoId']
            result = {
                'title': title,
                'thumbnail': thumbnail,
                'id': videoID
            }
            results.append(result)
        return results

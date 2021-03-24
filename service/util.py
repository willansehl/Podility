import os

class MetadataService:
    def get_metadata():
        app_name = os.getenv('HEROKU_APP_NAME', 'UNKNOWN_NAME')
        commit_hash = os.getenv("HEROKU_SLUG_COMMIT", "UNKNOWN_COMMIT_HASH")
        release_timestamp = os.getenv('HEROKU_RELEASE_CREATED_AT', 'UNKNOWN_RELEASE_TIME')
        commit_url = 'https://github.com/hcivideodj/app/commit/' + commit_hash

        return {
            'metameta': 'This is deployment information only available on remote Heroku environments.',
            'app_name': app_name,
            'commit_hash': commit_hash,
            'commit_url': commit_url,
            'release_timestamp': release_timestamp
        }

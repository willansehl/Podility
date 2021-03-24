class ChatMessage:
    def __init__(self, user, msg):
        self.user = user
        self.msg = msg

    def json(self):
        return {'username': self.user, 'message': self.msg}

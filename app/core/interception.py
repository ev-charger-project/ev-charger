from sqlalchemy import event
from sqlalchemy.orm import Session


class Interception:
    @staticmethod
    @event.listens_for(Session, "before_attach")
    def before_attach(session, instance):
        pass

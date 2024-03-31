from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import relationship, sessionmaker, Session
from typing import List
import sqlalchemy
import hashlib
from datetime import datetime
from credentials_local import creds


Base = sqlalchemy.orm.declarative_base()


class UserAction(Base):
    __tablename__ = 'user_actions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime)
    input_text = Column(String)
    output_text = Column(String)
    cost = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    login = Column(String)
    password = Column(String)
    balance = Column(Integer)
    actions = relationship("UserAction", backref="user")

    def set_password(self, password: str):
        """Set user's password"""
        self.password = hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password: str) -> bool:
        """Check if the given password is correct"""
        return self.password == hashlib.sha256(password.encode()).hexdigest()

    @classmethod
    def register(cls, session, login: str, password: str):
        """Register a new user"""
        if session.query(cls).filter_by(login=login).first() is not None:
            raise ValueError("User with this login already exists")

        user = cls(login=login, balance=0)
        user.set_password(password)
        session.add(user)
        session.commit()
        return user

    @classmethod
    def authenticate(cls, session, login: str, password: str):
        """Authenticate a user"""
        try:
            user = session.query(cls).filter_by(login=login).one()
            if user.check_password(password):
                return user
            else:
                return None
        except NoResultFound:
            return None

    def check_balance_sufficient(self, amount: int) -> bool:
        """Check if the user's balance is sufficient for a given amount"""
        return self.balance >= amount
    
    def increase_balance(self, session, amount: int):
        """Increase user's balance by given amount"""
        self.balance += amount

        try:
            user = session.query(User).filter_by(id=self.id).one()
            user.balance = self.balance
            session.merge(user)
            session.commit()
        except NoResultFound:
            session.rollback()

    def make_action(self, session, input_text: str, output_text: str):
        try:
            user = session.query(User).filter_by(id=self.id).one()
            user.balance -= len(output_text)
            session.merge(user)
            session.commit()

            action = UserAction(
                date=datetime.now(),
                input_text=input_text,
                output_text=output_text,
                cost=len(output_text),
                user_id=self.id
            )
            session.add(action)
            session.commit()
        except NoResultFound:
            session.rollback()

    def get_history(self, session) -> List[UserAction]:
        """Returns the user's action history"""
        try:
            history = session.query(UserAction).filter_by(user_id=self.id).order_by(UserAction.date.desc()).all()
            return history
        except NoResultFound:
            return []


if __name__ == "__main__":
    engine = create_engine(creds["db_url"])
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    # Test
    session = Session()

    new_user = User.register(session, login="ivanaleksa", password="123")
    
    new_user.increase_balance(session, 100)
    new_user.make_action(session, "I want summarize!", "Here it is!")
    print(new_user.get_history(session))
    print(new_user.check_balance_sufficient(50))

    session.close()
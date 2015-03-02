import redis
from datetime import datetime

from flask import Flask, Response, render_template, url_for, flash, request
from flask.ext.sqlalchemy import SQLAlchemy

from wtforms import *
from flask.ext.wtf import Form

from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/msgs.db'
app.config['SECRET_KEY'] = 'blah'
db = SQLAlchemy(app)
r = redis.StrictRedis()


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text)
    to = db.Column(db.Integer, nullable=False, index=True)

    unread = db.Column(db.Boolean, default=True)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)


    def __repr__(self):
        return 'To: id<{}> \n Sub: {}'.format(self.to, self.subject)

    def save(self):
        db.session.add(self)
        db.session.commit()


class ShowInterestForm(Form):
    show_interest = SubmitField('Show Interest')


@app.route('/')
def user_list():
    print url_for('users', id=100)
    print "<a href='{}'>Talent {}<a>".format(url_for('users', id=55), 55)
    s = '</br>'.join("<a href='{}'>Talent {}<a>".format(url_for('users', id=id), id) for id in range(10))
    return Response(s)

@app.route('/users/<int:id>', methods=['GET', 'POST'])
def users(id):
    form = ShowInterestForm()
    if form.validate_on_submit():
        msg = Message(to=id, subject='Interest shown', content='Somebody has shown interest to user {}'.format(id))
        msg.save()
        r.publish('msg:{}'.format(id), msg)
        flash('Thanks for showing interest.')
    return render_template('user.html', id=id, form=form)


@app.route('/users/<id>/inbox')
def inbox(id):
    msgs = Message.query.filter_by(to=id).order_by('sent_at').all()
    return render_template('inbox.html', id=id, msgs=msgs)


class MessagesNamespace(BaseNamespace):
    def initialize(self):
        self.logger = app.logger
        self.log("Socketio session started")

    def log(self, message):
        self.logger.info("[{0}] {1}".format(self.socket.sessid, message))

    def on_join(self, user_id):
        print 'User #{} has joined'.format(user_id)
        self.room = 'msg:{}'.format(user_id)
        self.pubsub = r.pubsub()
        self.pubsub.subscribe('msg:{}'.format(user_id))
        self.spawn(self.listener)
        return True

    def listener(self):
        for item in self.pubsub.listen():
            self.emit('newmsg', item['data'])


@app.route('/socket.io/<path:remaining>')
def socketio(remaining):
    try:
        socketio_manage(request.environ, {'/msgs': MessagesNamespace}, request)
    except:
        app.logger.error("Exception while handling socketio connection",
                         exc_info=True)
    return Response()

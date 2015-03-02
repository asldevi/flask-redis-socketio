
from socketio.server import SocketIOServer
from webapp import app, db

from gevent import monkey; monkey.patch_all()

if __name__ == '__main__':
    db.create_all()
    print 'Listening on port http://127.0.0.1:8080 and on port 10843 (flash policy server)'
    SocketIOServer(('', 8080), 
        app,
        resource="socket.io", 
        policy_server=True,
        policy_listener=('0.0.0.0', 10843)).serve_forever()

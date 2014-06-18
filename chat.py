#!/bin/env python
from gevent import monkey
monkey.patch_all()
from app import create_app, socketio

app = create_app(True)

if __name__ == '__main__':
    socketio.run(app)

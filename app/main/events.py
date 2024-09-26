from time import time
from flask_socketio import emit, join_room, leave_room
from .. import socketio
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from base64 import b64decode
from cryptography.hazmat.primitives import padding
from flask import session


# Encryption parameters
key = b'12345678901234567890123456789012'  # 256-bit key
iv = b'1234567890123456'  # 128-bit IV

def decrypt_message(encrypted_message):
    print('recieved at flask - ' + encrypted_message)
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    padded_message = decryptor.update(b64decode(encrypted_message)) + decryptor.finalize()

    # Unpad the message (PKCS7 padding)
    pad_len = padded_message[-1]
    message = padded_message[:-pad_len].decode('utf-8')
    print('decrypted at flask - ' + message)
    return message

def encrypt_message(message):
    backend = default_backend()

    padder = padding.PKCS7(128).padder()
    padded_message = padder.update(message) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()

    encrypted_message = encryptor.update(padded_message) + encryptor.finalize()

    encrypted_message_b64 = b64decode(encrypted_message).decode('utf-8')

    print('encrypted message - ' + encrypted_message_b64)
    return encrypted_message_b64

@socketio.on('text', namespace='/chat')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('room')
    decrypted_msg = decrypt_message(message['msg'])

    #use the message at the server side and do whatever needed. 
    #encrypt again to send back
    
    #encrypted_msg = encrypt_message(decrypt_message)
    #print('encrypted msg agin - '+ encrypt_message)
    
    emit('message', {
        'msg': f"{session.get('name')}: {decrypted_msg}",
    }, to=room)

@socketio.on('joined', namespace='/chat')
def joined(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    join_room(room)
    emit('status', {
        'msg': f"{session.get('name')} has entered the room.",
    }, to=room)

@socketio.on('left', namespace='/chat')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    emit('status', {
        'msg': f"{session.get('name')} has left the room.",
    }, to=room)
import time
from database.sqlite import get_session_expiration_timestamp, delete_session

def session_id_valid(session_id: str):
    expiration_timestamp = get_session_expiration_timestamp(session_id)

    if not expiration_timestamp:
        return False

    current_timestamp = int(time.time())

    if current_timestamp > expiration_timestamp:
        delete_session(session_id)
        return False

    return True

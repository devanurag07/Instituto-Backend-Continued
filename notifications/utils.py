def ws_response(event, data, msg):
    return {
        "type": event,
        "payload": data,
        "msg": msg,
        "code": 200
    }

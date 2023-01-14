# # teacher,student - global
# NOTI_STD_LEFT_BATCH = "noti.teacher.std.left"
# NOTI_STD_JOINED_BATCH = "noti.teacher.std.joined"
# NOTI_STD_REQUEST_RECEIVED = "noti.std.request.received"


# # Teacher -> Student
# NOTI_ADDED_TO_BATCH = "noti.added.to.batch"
# NOTI_REMOVED_FROM_BATCH = "noti.removed.from.batch"


# # Owner -> Teacher
# NOTI_TEACHER_REQUEST_ACCEPTED = "noti.teacher.request.accepted"
# NOTI_TEACHER_REQUEST_DENIED = "noti.teacher.request.denied"
# NOTI_MEETING_ANNOUNCEMENT = "noti.meeting.announcement"
# NOTI_TEACHER_SUBJECT_ASSIGNED = "noti.teacher.batch.created"

# # Owner
# NOTI_TEACHER_REQUEST_RECEIVED = "noti.teacher.request.received"
# NOTI_TEACHER_BATCH_CREATED = "noti.teacher.batch.created"

import json


def ws_response(event="", data={}, msg="", code=200):
    return json.dumps({
        "type": event,
        "payload": data,
        "msg": msg,
        "code": code
    })

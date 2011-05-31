USERS = {
    'admin': ['group:admin'],
    'user': []
}

def findgroup(userid, request):
    if userid in USERS:
        return USERS[userid]

USERS = {
    'admin': ['group:admin'],
    'user': []
}

def groupfinder(userid, request):
    if userid in USERS:
        return USERS[userid]

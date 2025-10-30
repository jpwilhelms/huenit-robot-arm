import json

def send_event(data):
    fake_log_add()
    data.update({'sender': 'python'})
    print(json.dumps(data))


def fake_log_add():
    print('fake_log')
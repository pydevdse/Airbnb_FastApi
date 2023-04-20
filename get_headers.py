import json


def get_headers(filename='headers.txt'):
    filename = 'headers/' + filename
    try:
        headers = open(filename, 'r').read().split('\n')
    except:
        return
    headers = [h for h in headers if h != ""]
    headers_json = {}
    for h in headers:
        if h[0] == ':': continue
        index = h.find(':')
        line = h
        headers_json.update({
            line[0:index].strip(): line[index + 1:].strip()
        })
    return headers_json


if __name__ == '__main__':
    print(json.dumps(get_headers("headers_room.txt"), indent=4))

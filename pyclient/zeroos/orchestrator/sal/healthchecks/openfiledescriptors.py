import json


def main():
    messages = [{
        'id': 'openfiledescriptors',
        'name': 'openfiledescriptors',
        'resource': 'System Load',
        'status': 'OK',
        'category': 'System',
        'message': 'All openfilescriptors are ok'
    }]
    print(json.dumps(messages))


if __name__ == '__main__':
    main()

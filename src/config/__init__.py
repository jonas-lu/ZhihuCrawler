import json
import os


APP_ROOT = os.path.dirname(os.path.abspath(__file__)) + '/../../'
with open(APP_ROOT + 'config.json') as f:
    _config = json.loads(f.read())
    _config['root'] = APP_ROOT


def get(entry):
    if not entry:
        return _config
    else:
        keys = entry.split('.')
        ret = _config
        for i in range(len(keys)):
            ret = ret[keys[i]]

        return ret


def set_config(key, val):
    _config[key] = val


if __name__ == '__main__':
    print(get('queue.task_user'))
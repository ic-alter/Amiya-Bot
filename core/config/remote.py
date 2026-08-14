import requests
from dataclasses import dataclass, field
from core.util import init_config_file


@dataclass
class Remote:
    cos: str = 'https://cos.amiyabot.com'
    plugin: str = 'https://cdn.amiyabot.com'
    console: str = 'http://106.52.139.57:8000'
    
    def __init__(self):
        try:
            res = requests.get(f'{self.plugin}/api/v1/remote')
            data = res.json()
            if res.status_code != 200 or not 'code' in data:
                return
            if data['code'] == 200:
                self.cos = data['data']['cos']
                self.plugin = data['data']['plugin']
                self.console = data['data']['console']
        except:
            pass


@dataclass
class RemoteConfig:
    remote: Remote = field(default_factory=Remote)


def init(file: str) -> RemoteConfig:
    return init_config_file(file, RemoteConfig, True)


remote_config = init('config/remote.yaml')

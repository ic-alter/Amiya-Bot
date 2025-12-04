from dataclasses import dataclass, field
from core.util import init_config_file


@dataclass
class Penetration:
    ports: dict = field(default_factory=dict)


def init(file: str) -> Penetration:
    return init_config_file(file, Penetration)


penetration_config = init('config/penetration.yaml')

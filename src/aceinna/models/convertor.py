from dataclasses import dataclass, field
from typing import List, Optional
from .data_source import DataSource, CommonCANDataSource, J1939DataSource
from .convert_rule import ConvertRule

@dataclass
class Convertor:
    name: str
    data_source: Optional[DataSource] = None
    convert_rules: List[ConvertRule] = field(default_factory=list)
    result_folder: str = ""

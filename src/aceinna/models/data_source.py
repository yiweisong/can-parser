from dataclasses import dataclass, field
from typing import List, Optional, Union, Literal

@dataclass
class FieldSetting:
    name: str
    start_bit: int
    length: int
    byte_order: Literal['little_endian', 'big_endian'] = 'little_endian'
    value_type: Literal['unsigned', 'signed', 'float', 'double'] = 'unsigned'
    factor: float = 1.0
    offset: float = 0.0
    unit: str = ""

@dataclass
class MessageMapping:
    identifier: int  # CAN ID or PGN
    fields: List[FieldSetting] = field(default_factory=list)

@dataclass
class DataSource:
    name: str # The design implies a name might be useful, though not explicitly listed under DataSource fields in the outline, it's good for identification. Or maybe the Convertor holds the name. The Convertor has a name. The UI for DataSource Editor implies it's part of a Convertor.
    # Actually, the DataSource is a component of a Convertor.
    type: Literal['common_can', 'j1939']
    dbc_file_path: str = ""

@dataclass
class CommonCANDataSource(DataSource):
    message_mappings: List[MessageMapping] = field(default_factory=list)
    type: Literal['common_can'] = 'common_can'

@dataclass
class J1939DataSource(DataSource):
    pgn_mappings: List[MessageMapping] = field(default_factory=list)
    source_address_filters: List[int] = field(default_factory=list)
    type: Literal['j1939'] = 'j1939'

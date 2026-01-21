from dataclasses import dataclass
from typing import Literal

@dataclass
class DataSourceFetchRule:
    name: str
    file_type: Literal['xlsx', 'csv']
    message_id_col_index: int
    message_data_col_index: int
    timestamp_col_index: int

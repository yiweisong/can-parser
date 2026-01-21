from dataclasses import dataclass, field
from typing import List, Optional, Union, Literal

@dataclass
class ConvertRule:
    type: Literal['plot', 'data_list']

@dataclass
class AxisBinding:
    binding: str # data field name

@dataclass
class PlotRule(ConvertRule):
    title: str = ""
    x_axis: Optional[AxisBinding] = None # data field name or None for index
    y_axes: List[AxisBinding] = field(default_factory=list)
    
    # Styles
    figure_figsize: tuple = (6.4, 4.8)
    figure_dpi: int = 160
    grid_linestyle: str = "--"
    grid_alpha: float = 0.5
    tick_labelsize: int = 8
    legend_label: str = "legend1" # This seems weird in design "label, loc, fontsize". Usually legend labels come from data series.
    legend_loc: Union[str, int] = "best"
    legend_fontsize: int = 8
    
    type: Literal['plot'] = 'plot'

@dataclass
class DataListField:
    binding: str

@dataclass
class DataListRule(ConvertRule):
    fields: List[DataListField] = field(default_factory=list)
    delimiter: str = ","
    include_header: bool = True
    type: Literal['data_list'] = 'data_list'

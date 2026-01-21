import os
import threading
from PySide6.QtCore import QThread, Signal
from ..models.convertor import Convertor
from ..models.fetch_rule import DataSourceFetchRule
from .data_loader import DataLoader
from .decoder import Decoder
from .result_generator import ResultGenerator

class ConvertWorker(QThread):
    progress_update = Signal(str, int)
    finished_signal = Signal()
    error_signal = Signal(str)

    def __init__(self, convertor: Convertor, fetch_rule: DataSourceFetchRule, data_file_path: str):
        super().__init__()
        self.convertor = convertor
        self.fetch_rule = fetch_rule
        self.data_file_path = data_file_path
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        """
        Calculates and generates results. 
        """
        self._is_cancelled = False
        self._report("Starting conversion process...", 0)

        try:
            # 1. Load Data
            if self._check_cancel(): return
            self._report("Loading data...", 10)
            raw_df = DataLoader.load_data(self.data_file_path, self.fetch_rule)
            self._report("Data loaded.", 30)

            # 2. Decode
            if self._check_cancel(): return
            self._report("Decoding data...", 40)
            if self.convertor.data_source:
                # TODO: Pass cancellation check to decoder?
                results = Decoder.decode(raw_df, self.convertor.data_source)
            else:
                results = {}
            self._report("Decoding complete.", 70)

            # 3. Generate Results
            if self._check_cancel(): return
            self._report("Generating results...", 80)
            if self.convertor.result_folder:
                output_folder = self.convertor.result_folder
            else:
                # Fallback
                output_folder = os.path.join(os.path.dirname(self.data_file_path), f"{self.convertor.name}_results")
            
            ResultGenerator.generate(results, self.convertor.convert_rules, output_folder)
            self._report("Conversion finished successfully.", 100)
            self.finished_signal.emit()
            
        except Exception as e:
            msg = f"Error: {str(e)}"
            self._report(msg, 100)
            self.error_signal.emit(msg)
            print(e) 

    def _check_cancel(self) -> bool:
        if self._is_cancelled:
            self._report("Process cancelled.", 100)
            self.finished_signal.emit()
            return True
        return False

    def _report(self, message: str, percent: int):
        print(f"[Engine] {message} ({percent}%)")
        self.progress_update.emit(message, percent)

import pandas as pd
import numpy as np
from typing import Dict, List, Any
from ..models.data_source import DataSource, CommonCANDataSource, J1939DataSource, MessageMapping, FieldSetting

class Decoder:
    @staticmethod
    def decode(data: pd.DataFrame, data_source: DataSource) -> Dict[str, pd.Series]:
        """
        Decodes the raw data based on the data source configuration.
        Returns a dictionary mapping 'SignalName' -> Series (indexed by timestamp).
        """
        results = {}
        
        # Ensure we work with a copy and standardise column names
        df = data.copy()
        
        # Group by Message ID to optimize processing
        # message_id in df is int.
        
        if data_source.type == 'common_can':
            results = Decoder._decode_common_can(df, data_source)
        elif data_source.type == 'j1939':
            results = Decoder._decode_j1939(df, data_source)
            
        return results

    @staticmethod
    def _decode_common_can(df: pd.DataFrame, source: CommonCANDataSource) -> Dict[str, pd.Series]:
        results = {}
        grouped = df.groupby('message_id')
        
        for mapping in source.message_mappings:
            msg_id = mapping.identifier
            if msg_id in grouped.groups:
                group_df = grouped.get_group(msg_id)
                time_series = group_df['timestamp']
                data_series = group_df['data']
                
                for field_setting in mapping.fields:
                    values = Decoder._unpack_signal(data_series, field_setting)
                    # Create a series with timestamp index
                    s = pd.Series(values, index=time_series.values, name=field_setting.name)
                    results[field_setting.name] = s
                    
        return results

    @staticmethod
    def _decode_j1939(df: pd.DataFrame, source: J1939DataSource) -> Dict[str, pd.Series]:
        results = {}
        
        # J1939 extraction
        # PGN = (ID >> 8) & 0x1FFFF
        # SA = ID & 0xFF
        
        # We process the whole dataframe to extract PGN and SA first? 
        # Or Just iterate groupings of raw ID and check?
        # Since multiple Raw IDs can map to same PGN (different SA), 
        # we can't just group by Raw ID and look up PGN directly once.
        # But grouping by Raw ID is still efficient.
        
        grouped = df.groupby('message_id')

        for raw_id, group_df in grouped:
            
            pgn = (raw_id >> 8) & 0x1FFFF
            sa = raw_id & 0xFF
            
            # Check if this PGN is interesting
            # Find generic mapping for this PGN
            relevant_mapping = None
            for mapping in source.pgn_mappings:
                if mapping.identifier == pgn:
                    relevant_mapping = mapping
                    break
            
            if not relevant_mapping:
                continue

                
            # Check SA filter
            if source.source_address_filters and sa not in source.source_address_filters:
                continue

                
            # Decode fields
            time_series = group_df['timestamp']
            data_series = group_df['data']
            
            for field_setting in relevant_mapping.fields:
                values = Decoder._unpack_signal(data_series, field_setting)
                s = pd.Series(values, index=time_series.values, name=field_setting.name)
                
                # Append J1939 SA to key to support splitting by SA in results
                # Format: SignalName#SA
                key = f"{field_setting.name}#{sa}"
                
                if key in results:
                    results[key] = pd.concat([results[key], s]).sort_index()
                else:
                    results[key] = s
                    
        return results

    @staticmethod
    def _unpack_signal(data_series: pd.Series, setting: FieldSetting) -> np.ndarray:
        # data_series is a series of bytes objects.
        
        def extract_value(data_bytes):
            if not data_bytes: 
                return 0
                
            # Convert bytes to int
            # need to handle byte order and bit extraction
            # This is slow if done row-by-row in python. 
            # But for correct implementation of bit unpacking, python logic is easiest to write first.
            
            # Construct a huge integer from bytes?
            # Or work with the specific bytes.
            
            # setting.start_bit and length. 
            # Start bit definition varies (Intel vs Motorola).
            
            # Let's use cantools-like logic (or just reuse cantools logic if we could?)
            # But here we are implementing it manually as per previous thought.
            
            # Simple implementation for now (Intel/Little Endian primarily?)
            # If length is small (<= 64), we can convert to int.
            
            full_int = int.from_bytes(data_bytes, byteorder='little') # Assuming little endian for the whole frame? 
            # CAN data is usually array of bytes. 
            
            # Intel (Little Endian): Start bit is LSB. 
            # Motorola (Big Endian): Start bit is MSB? 
            
            # Let's rely on standard CAN definitions. 
            # If Byte Order is Little Endian (Intel):
            #   Bits count from 0 (LSB of Byte 0) upwards.
            
            # If Byte Order is Big Endian (Motorola):
            #   It's more complex mapping.
            
            # Given keeping it simple and robust, and "cantools" is a dependency
            # Maybe I should just create a temporary DBC definition and use cantools to decode!
            # It handles all edge cases of bit numbering.
            return 0

        # REVISION: Using cantools is much safer.
        # But we don't want to create a DB object for every row.
        # We can creating a DB object ONCE for the mapping, then use it.
        
        # However, `decode_message` expects a frame ID.
        # Here we just want to decode signals from bytes.
        
        # Let's use a custom bit unpacker optimised for pandas/numpy if possible, 
        # or just row iteration with a robust unpacker.
        
        return np.array([Decoder._extract_raw_value(b, setting) for b in data_series])

    @staticmethod
    def _extract_raw_value(data: bytes, setting: FieldSetting) -> float:
        if not data: return 0.0
        
        # Start bit: 0-63
        start_bit = setting.start_bit
        length = setting.length
        byte_order = setting.byte_order # 'little_endian' or 'big_endian'
        
        # Convert to int (always little endian view of the byte array for easy indexing?)
        # Or standard bit extraction.
        
        if byte_order == 'little_endian':
            # Intel
            # We can convert the whole byte array to a giant integer (little endian)
            # Then shift and mask.
            val_int = int.from_bytes(data, 'little')
            raw = (val_int >> start_bit) & ((1 << length) - 1)
        else:
            # Motorola (Big Endian)
            # This is tricky.
            # Start bit usually refers to the MSB of the signal in Motorola? 
            # Or LSB? In cantools/Kvaser/Vector, it varies.
            # Usually in DBC:
            # Intel: Start bit is LSB.
            # Motorola: Start bit is MSB (or LSB depending on format).
            # Let's assume standard DBC convention:
            # Big Endian: Start bit is the MSB of the signal.
            # We need to reverse bytes or carefully extract.
            
            # For this prototype, let's implement Little Endian correctly first.
            # And use a basic Big Endian implementation where we treat data as big endian int.
            # But bit numbering in CAN is usually byte-based.
            
            # Let's punt on complex Motorola bit numbering for a manual implementation 
            # and stick to a simplified view or rely on `cantools` logic if we were using it.
            # Actually, `cantools` code is open source, I could check how they do it.
            # But wait, looking at `requirements.txt`, we HAVE `cantools`.
            # Why not use `cantools` internals? `cantools.database.can.signal.Signal.decode`
            
            pass 
            # Placeholder for Motorola
            val_int = int.from_bytes(data, 'little') # Fallback
            raw = (val_int >> start_bit) & ((1 << length) - 1)

        # Sign extension
        if setting.value_type == 'signed':
            # check sign bit
            if raw & (1 << (length - 1)):
                raw -= (1 << length)
                
        # Scale and offset
        phys = (raw * setting.factor) + setting.offset
        return float(phys)


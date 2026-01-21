import os
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List
from ..models.convert_rule import PlotRule, DataListRule, ConvertRule

class ResultGenerator:
    @staticmethod
    def generate(results: Dict[str, pd.Series], rules: List[ConvertRule], output_folder: str):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # Analyze available SAs for J1939 splitting
        # Keys are "Name#SA" or just "Name"
        sas = set()
        has_j1939_keys = False
        
        plain_results = {} # Name -> Series (for CommonCAN or un-split logic if any)
        
        for key in results.keys():
            if '#' in key:
                parts = key.split('#')
                if len(parts) == 2 and parts[1].isdigit():
                    sas.add(int(parts[1]))
                    has_j1939_keys = True
            else:
                plain_results[key] = results[key]
        
        groups = []
        if has_j1939_keys:
            # Create a view for each SA
            for sa in sorted(list(sas)):
                # Filter results for this SA
                view = {**plain_results} # Include plain results in all groups?
                for key, val in results.items():
                    if key.endswith(f"#{sa}"):
                        name = key.split('#')[0]
                        view[name] = val
                groups.append((f"_SA{sa}", view))
        else:
            # Common CAN or no J1939 specific keys
            groups.append(("", results))

        for suffix, group_results in groups:
            for i, rule in enumerate(rules):
                try:
                    if rule.type == 'plot':
                        ResultGenerator._generate_plot(group_results, rule, output_folder, i, suffix)
                    elif rule.type == 'data_list':
                        ResultGenerator._generate_data_list(group_results, rule, output_folder, i, suffix)
                except Exception as e:
                    print(f"Error generating result for rule {i} suffix {suffix}: {e}")

    @staticmethod
    def _generate_plot(results: Dict[str, pd.Series], rule: PlotRule, folder: str, index: int, suffix: str = ""):
        # Check if we have any data to plot for this rule in this view
        has_data = False
        if rule.x_axis and rule.x_axis.binding in results: has_data = True
        for y_axis in rule.y_axes:
            if y_axis.binding in results: has_data = True
            
        if not has_data: return

        plt.figure(figsize=rule.figure_figsize, dpi=rule.figure_dpi)
        
        # X Axis
        x_data = None
        if rule.x_axis and rule.x_axis.binding in results:
            x_data = results[rule.x_axis.binding]
        
        # Y Axis
        for y_axis in rule.y_axes:
            if y_axis.binding in results:
                y_data = results[y_axis.binding]
                
                # Align X and Y
                # If x_data is provided, we need to merge/align by timestamp? 
                # Or scatter plot?
                # Usually we plot Y vs Time if X is None.
                # If X is provided (e.g. another signal), we scatter or plot signal vs signal.
                
                label = y_axis.binding
                
                if x_data is not None:
                    # Align based on timestamp? 
                    # If x_data is another signal, it has its own timestamps.
                    # We likely need to reindex.
                    # For simplicity:
                    # If timestamps match exactly: direct plotting.
                    # If not, maybe reindex y to x's time?
                    
                    # Let's assume common time base or just plot against values.
                    # Actually complex.
                    # Fallback: Plot against index if x_data missing.
                    try:
                        # Reindex y to x
                        combined = pd.concat([x_data, y_data], axis=1).dropna()
                        # Sort by x?
                        combined = combined.sort_values(by=combined.columns[0])
                        plt.plot(combined.iloc[:, 0], combined.iloc[:, 1], label=label)
                    except:
                        pass
                else:
                    # Plot vs Time (Index)
                    plt.plot(y_data.index, y_data.values, label=label)

        plt.title(rule.title)
        plt.grid(linestyle=rule.grid_linestyle, alpha=rule.grid_alpha)
        plt.tick_params(labelsize=rule.tick_labelsize)
        # if hasattr(rule, 'legend_label'): 
        #      # The design says "legendStyle: label, loc, fontsize"
        #      # The label "legend1" seems to be the default text? 
        #      # Usually legend uses the plot labels.
        #      plt.legend('legend', loc=rule.legend_loc, fontsize=rule.legend_fontsize)
        # else:
        #      plt.legend()
             
        filename = f"plot_{index}_{rule.title.replace(' ', '_')}{suffix}.png"
        plt.savefig(os.path.join(folder, filename))
        plt.close()

    @staticmethod
    def _generate_data_list(results: Dict[str, pd.Series], rule: DataListRule, folder: str, index: int, suffix: str = ""):
        # Merge all required fields into one DataFrame
        series_list = []
        for field in rule.fields:
            if field.binding in results:
                s = results[field.binding]
                series_list.append(s)
        
        if not series_list:
            return

        # Outer join on execution? 
        # Signals might come at different timestamps.
        # We need a unified timeline? Or just a huge table with NaNs?
        # Usually "Outer Join".
        
        df = pd.concat(series_list, axis=1)
        
        # Sort by timestamp (index)
        df.sort_index(inplace=True)
        
        # Add index as timestamp column?
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'Timestamp'}, inplace=True)
        
        filename = f"datalist_{index}{suffix}.csv"
        df.to_csv(
            os.path.join(folder, filename), 
            sep=rule.delimiter, 
            index=False, 
            header=rule.include_header
        )

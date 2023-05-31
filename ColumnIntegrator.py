from mimetypes import init
import tkinter as tk
import tkinter.font as tk_font
import tkinter.messagebox as msg
import re
import tkinterdnd2 as dnd
import pandas as pd
import csv
import copy
from enum import auto, IntEnum


MSG_INFO = """
  Information

1. 본 프로그램의 시간순 정렬은
time -> Time -> GlobalTime
의 우선 순위로 찾아낸 트렌드를 기준으로 정렬합니다.

2. 본 프로그램은 센서와 바코드를 동시에 고려하여
sensorID -> SensorID
barcode -> Barcode
의 우선 순위로 찾아낸 트렌드를 기준으로 정렬합니다.

3. 파일명을 포함하여 경로상에 }, {를 포함할 수 없습니다.

제작자 : 

"""
class EnumFromZero(IntEnum) :
    def _generate_next_value_(name, start, count, last_values) :
        return count

    def __str__(self) :
        return self.name

    def __repr__(self) :
        return self.name

class DUPLICATE_OPTION(EnumFromZero) :
    DO_NOT_DROP = auto()
    LEAVE_FIRST_FROM_EACH_LOT = auto()
    LEAVE_LAST_FROM_EACH_LOT = auto()
    LEAVE_FIRST_FROM_WHOLE = auto()
    LEAVE_LAST_FROM_WHOLE = auto()

class UiMgr :
    def __init__(self) :
        
        self.__root = dnd.Tk()
        self.__root.title("Column Integrator")
        self.__root.geometry("640x600+100+100")
        self.__root.resizable(False, False)

        self.__font_title = tk_font.Font(family = "Consolas", size = 17)

        self.__list_full_path = []
        self.__list_file = []

        self.__var_duplicate = tk.IntVar()
        
        self.regex_file = re.compile("([a-zA-Z]{1}:[^}{]+?)([^/]+?\.[cC][sS][vV])")

    def get_var_duplicate(self) -> int :
        return self.__var_duplicate.get()

    def __add_listbox(self, event) :
        event_data_preproc = event.data.replace("\\", "/")
        files_found = self.regex_file.findall(event_data_preproc)
        for file in files_found :
            full_path_temp = file[0]+file[1]
            if full_path_temp in self.__list_full_path : continue
            self.__list_full_path.append(full_path_temp)
            self.__list_file.append(file[1])
            self.list_box.insert(tk.END, file[1])

    def __clear(self) :
        self.list_box.delete(0, tk.END)
        self.__list_full_path.clear()
        self.__list_file.clear()

    def __execute_integration(self) :
        if len(self.__list_full_path) == 0 :
            msg.showinfo("Info", "List is empty")
            return
        try :
            for file_path in self.__list_full_path :
                column_integrator = ColumnIntegrator(file_path)
                column_integrator.execute()
            msg.showinfo("Info", "Integration complete")
        except Exception as e :
            msg.showerror("Error", "Error occurred : " + str(e))

    def __show_info(self) :
        msg.showinfo("Info", MSG_INFO)

    def run_ui(self) :

        self.frame_title = tk.Frame(self.__root, height = 15)
        self.frame_title.pack(fill = "x", padx = 10, pady = 10)
        
        self.label_title = tk.Label(self.frame_title, text = "Column Integrator", font = self.__font_title)
        self.label_title.pack(fill = "x")

        self.frame_listbox = tk.Frame(self.__root)
        self.frame_listbox.pack(fill = "x", padx = 10, pady = 10)

        self.scrollbar_listbox = tk.Scrollbar(self.frame_listbox)
        self.scrollbar_listbox.pack(side = "right", fill = "y")
        
        self.list_box = tk.Listbox(self.frame_listbox, selectmode = "extended", height = 20, yscrollcommand=self.scrollbar_listbox.set)
        self.list_box.pack(side = "left", fill = "both", expand = True, padx = 10)
        self.scrollbar_listbox.config(command = self.list_box.yview)
        self.list_box.drop_target_register(dnd.DND_FILES)
        self.list_box.dnd_bind("<<Drop>>", self.__add_listbox)
        
        self.frame_duplicate_button = tk.Frame(self.__root)
        self.frame_duplicate_button.pack(fill = "x", padx = 10, pady = 10)
        
        self.radio_button_duplicate_1 = tk.Radiobutton(self.frame_duplicate_button, text = "중복 제거 하지 않음", value = int(DUPLICATE_OPTION.DO_NOT_DROP), variable = self.__var_duplicate)
        self.radio_button_duplicate_1.select()
        self.radio_button_duplicate_2 = tk.Radiobutton(self.frame_duplicate_button, text = "각 랏의 첫 검사만 남기고 중복 제거", value = int(DUPLICATE_OPTION.LEAVE_FIRST_FROM_EACH_LOT), variable = self.__var_duplicate)
        self.radio_button_duplicate_3 = tk.Radiobutton(self.frame_duplicate_button, text = "각 랏의 마지막 검사만 남기고 중복 제거", value = int(DUPLICATE_OPTION.LEAVE_LAST_FROM_EACH_LOT), variable = self.__var_duplicate)
        self.radio_button_duplicate_4 = tk.Radiobutton(self.frame_duplicate_button, text = "랏 상관 없이 시간상 첫 검사만 남기고 중복 제거", value = int(DUPLICATE_OPTION.LEAVE_FIRST_FROM_WHOLE), variable = self.__var_duplicate)
        self.radio_button_duplicate_5 = tk.Radiobutton(self.frame_duplicate_button, text = "랏 상관 없이 시간상 마지막 검사만 남기고 중복 제거", value = int(DUPLICATE_OPTION.LEAVE_LAST_FROM_WHOLE), variable = self.__var_duplicate)
        self.radio_button_duplicate_1.grid(column = 0, row = 0, sticky = "w")
        self.radio_button_duplicate_2.grid(column = 0, row = 1, sticky = "w")
        self.radio_button_duplicate_3.grid(column = 0, row = 2, sticky = "w")
        self.radio_button_duplicate_4.grid(column = 0, row = 3, sticky = "w")
        self.radio_button_duplicate_5.grid(column = 0, row = 4, sticky = "w")

        self.frame_btn = tk.Frame(self.__root)
        self.frame_btn.pack(fill = "x", padx = 10, pady = 10)

        self.btn_exit = tk.Button(self.frame_btn, text = "Exit", width = 10, command = self.__root.quit)
        self.btn_exit.pack(side = "right", padx = 10)
        self.btn_clear = tk.Button(self.frame_btn, text = "Clear", width = 10, command = self.__clear)
        self.btn_clear.pack(side = "right", padx = 10)
        self.btn_run = tk.Button(self.frame_btn, text = "Run", width = 10, command = self.__execute_integration)
        self.btn_run.pack(side = "right", padx = 10)
        self.btn_info = tk.Button(self.frame_btn, text = "Info", width = 10, command = self.__show_info)
        self.btn_info.pack(side = "left", padx = 10)
        
        self.__root.mainloop()


class CsvFile :
    def __init__(self, file_name, no_header=False) :
        if no_header :
            f = open(file_name, encoding='utf-8')
            reader = csv.reader(f)
            csv_list = []
            for i in reader :
                csv_list.append(i)
            f.close()
            self.data = pd.DataFrame(csv_list)
        else : self.data = pd.read_csv(file_name)

    def print_out(self) :
        print(self.data)
    
    def remove_index(self) :
        drop_list = []
        for i in range(len(self.data)) :
            if(self.data.iloc[i][0] == self.data.columns[0]) :
                drop_list.append(i)
        
        self.data.drop(drop_list, axis = 0, inplace = True)
        self.data.reset_index(drop = True, inplace = True)
    
    def data_sort(self, idx) :
        self.data.sort_values(by = [idx], inplace = True, ascending = True, kind = 'quicksort', ignore_index = True)

    def data_duplicate(self, idx) :
        try :
            self.data.drop_duplicates(subset = idx, inplace = True, keep = "first", ignore_index = True)
        
        except :
            print("error")
    
    def data_to_csv(self, filename : csv) :
        self.data.to_csv(filename, index = None)

    def split_csv(self, row_begin, row_end) -> pd.DataFrame :
        ret_temp = self.data.iloc[row_begin:row_end,:]
        ret_temp.rename(columns=ret_temp.iloc[0], inplace=True)
        ret_temp.drop(ret_temp.index[0], inplace=True)
        ret_temp.reset_index(drop = True, inplace = True)
        ret_temp.dropna(how='all', axis='columns', inplace=True)

        return ret_temp


class ColumnIntegrator :
    def __init__(self, file_name : str) :
        self.log = CsvFile(file_name, no_header=True)
        self.__df_list = []
        self.__file_name = file_name

    def __sort_headers(self) -> pd.DataFrame :
        headers_list = []
        for df in self.__df_list :
            headers_list.append(list(df.columns))

        result = list(copy.deepcopy(headers_list[0]))
        for header in headers_list :
            for idx in range(0, len(header)) :
                if header[idx] in result : continue
                result.insert(result.index(header[idx - 1]) + 1, header[idx])

        return result

    def __find_header(self, headers : list, list_candidate : list) -> str :
        for candidate in list_candidate :
            if not candidate in headers :
                continue
            return candidate
        return list_candidate[-1]

    def execute(self) :
        split_start = 0
        for row in range(1, len(self.log.data)) :
            if self.log.data.iloc[row][0] != self.log.data.iloc[0][0] : continue
            self.__df_list.append(self.log.split_csv(row_begin=split_start, row_end=row))
            split_start = row
        self.__df_list.append(self.log.split_csv(row_begin=split_start, row_end=len(self.log.data)))

        self.__df_list.sort(key=lambda x : len(x.columns), reverse=True)
        result = pd.concat(self.__df_list, ignore_index=True)

        sorted_headers = self.__sort_headers()
        result = result.reindex(columns = sorted_headers)
        
        time_header = self.__find_header(headers = sorted_headers, list_candidate = ["time", "Time", "GlobalTime"])
        lotnum_header = self.__find_header(headers = sorted_headers, list_candidate = ["lotNum", "LotNum"])
        barcode_header = self.__find_header(headers = sorted_headers, list_candidate = ["barcode", "Barcode"])
        sensorid_header = self.__find_header(headers = sorted_headers, list_candidate = ["sensorID", "SensorID"])
        
        if (ui_mgr.get_var_duplicate() != int(DUPLICATE_OPTION.DO_NOT_DROP)) :
            result.sort_values(by = [time_header], inplace = True, ascending = True, kind = 'quicksort', ignore_index = True)

        match (ui_mgr.get_var_duplicate()) :
            case int(DUPLICATE_OPTION.DO_NOT_DROP) :
                pass
            case int(DUPLICATE_OPTION.LEAVE_FIRST_FROM_EACH_LOT) :
                result.drop_duplicates(subset = [lotnum_header, barcode_header, sensorid_header], inplace = True, keep = "first", ignore_index = True)
            case int(DUPLICATE_OPTION.LEAVE_LAST_FROM_EACH_LOT) :
                result.drop_duplicates(subset = [lotnum_header, barcode_header, sensorid_header], inplace = True, keep = "last", ignore_index = True)
            case int(DUPLICATE_OPTION.LEAVE_FIRST_FROM_WHOLE) :
                result.drop_duplicates(subset = [barcode_header, sensorid_header], inplace = True, keep = "first", ignore_index = True)
            case int(DUPLICATE_OPTION.LEAVE_LAST_FROM_WHOLE) :
                result.drop_duplicates(subset = [barcode_header, sensorid_header], inplace = True, keep = "last", ignore_index = True)
        
        result.to_csv(self.__file_name.replace(".csv", "_Result.csv").replace(".CSV", "_Result.csv"), index=None)


if __name__ == "__main__" :
    ui_mgr = UiMgr()
    ui_mgr.run_ui()
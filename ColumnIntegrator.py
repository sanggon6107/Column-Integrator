from mimetypes import init
import tkinter as tk
from tkinter import messagebox as msg
import tkinterdnd2 as dnd
import customtkinter as ck
from tkinter import font
import re
import pandas as pd
import csv
import copy
from enum import auto, IntEnum
from dataclasses import dataclass
from ctypes import windll
from DllMgrTemporaryModuleId import *


MSG_INFO = """
  Information

1. 본 프로그램의 시간 헤더 인식은
time -> Time -> GlobalTime
순서입니다.

2. 본 프로그램의 센서 아이디 및 바코드 헤더 인식은
sensorID -> SensorID
barcode -> Barcode
순서입니다.

3. 파일명을 포함하여 경로상에 }, {를 포함할 수 없습니다.

제작자 : 

"""

EXPLANATION_MSG_DEFAULT = "파일을 드래그하여 리스트에 추가할 수 있습니다. csv 확장자가 아닌 파일은 추가할 수 없습니다."

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

class IDENTIFICATION_OPTION(EnumFromZero) :
    SENSOR_ID = auto()
    BARCODE = auto()
    SENSOR_ID_AND_BARCODE = auto()
    AUTO = auto()

class SETTING(EnumFromZero) :
    NO = auto()
    YES = auto()

@dataclass
class ModuleInfo :
    sensorid : str = None
    barcode : str = None
    temporary_module_id : int = None

@dataclass
class ModuleIdentificationInfo :
    sensorid : str = None
    barcode : str = None
    sensorid_and_barcode : str = None
    auto : str = None

MODULE_IDENTIFICATION_MSG = ModuleIdentificationInfo(
    sensorid = "센서 아이디를 기준으로 모듈을 구분합니다.",
    barcode = "바코드를 기준으로 모듈을 구분합니다.", 
    sensorid_and_barcode = """센서 아이디와 바코드가 모두 같아야 동일 모듈로 구분합니다.
    OS Test 불량 등으로 인해 센서아이디가 0으로 기재되는 경우
    다른 테스트 데이터와 동일 모듈로 인식하지 못할 수 있습니다.""", 
    auto = """프로그램 내부 알고리즘을 사용합니다.
    센서 아이디와 바코드 중 하나가 적혀있지 않더라도 다른 데이터와 비교 및 추정하여
    동일 모듈을 식별할 수 있습니다."""
)


class TkWrapper(ck.CTk, dnd.TkinterDnD.DnDWrapper) :
    def __init__ (self, *args, **kwargs) :
        super().__init__(*args, **kwargs)
        self.TkdndVersion = dnd.TkinterDnD._require(self)
ck.set_appearance_mode("dark")
ck.set_default_color_theme("green")

class UiMgr :
    def __init__(self) :
        
        self.__root = TkWrapper()
        self.__root.title("Column Integrator")
        self.__root.geometry("700x900+100+100")
        self.__root.resizable(False, False)
        self.__root.overrideredirect(True)

        self.__font_title = ck.CTkFont(family = "Century Gothic", size = 24)
        self.__font_title_bold = ck.CTkFont(family = "Century Gothic", size = 24, weight = "bold")
        self.__font_listbox = font.Font(size = 15)

        self.__list_full_path = []
        self.__list_file = []
        self.__list_column_integrator : list[ColumnIntegrator] = []

        self.__var_identification = tk.IntVar()
        self.__var_duplicate = tk.IntVar()
        self.__var_check_autorun = tk.IntVar()
        self.__var_check_autoclear = tk.IntVar()

        self.__pre_x, self.__pre_y = self.__root.winfo_pointerxy()
        
        self.regex_file = re.compile("([a-zA-Z]{1}:[^}{:]+?)([^/]+?\.[cC][sS][vV])")

        self.exist_dll = True
        try :
            self.dll_mgr_temporary_module_id_go = DllMgrTemporaryModuleId("./MakeTemporaryModuleIdGo.dll")
        except :
            self.exist_dll = False
        
    def get_var_identification(self) -> int :
        return self.__var_identification.get()

    def get_var_duplicate(self) -> int :
        return self.__var_duplicate.get()

    def __set_window(self) :
        GWL_EXSTYLE = -20
        WS_EX_APPWINDOW = 0x00040000
        WS_EX_TOOLWINDOW = 0x00000080
        hwnd = windll.user32.GetParent(self.__root.winfo_id())
        style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style = style & ~WS_EX_TOOLWINDOW
        style = style | WS_EX_APPWINDOW
        res = windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        self.__root.wm_withdraw()
        self.__root.after(0, lambda: self.__root.wm_deiconify())

    def __start_move_window(self, event) :
        self.__pre_x = event.x
        self.__pre_y = event.y

    def __execute_window_movement(self, event):
        delta_x = event.x - self.__pre_x
        delta_y = event.y - self.__pre_y

        x_to_be = self.__root.winfo_x() + delta_x
        y_to_be = self.__root.winfo_y() + delta_y

        self.__root.geometry(f"+{x_to_be}+{y_to_be}")

    def __stop_move_window(self, event) :
        self.__pre_x = None
        self.__pre_y = None

    def __add_listbox(self, event) :
        event_data_preproc = event.data.replace("\\", "/")
        files_found = self.regex_file.findall(event_data_preproc)
        for file in files_found :
            full_path_temp = file[0]+file[1]
            if full_path_temp in self.__list_full_path : continue
            self.__list_full_path.append(full_path_temp)
            self.__list_column_integrator.append(ColumnIntegrator(full_path_temp))
            self.__list_file.append(file[1])
            self.list_box.insert(tk.END, file[1])
        if self.__var_check_autorun.get() == int(SETTING.YES) : self.__execute_integration()

    def __clear(self) :
        self.list_box.delete(0, tk.END)
        self.__list_full_path.clear()
        self.__list_file.clear()
        self.__list_column_integrator.clear()

    def __execute_integration(self) :
        if len(self.__list_full_path) == 0 :
            msg.showerror("Info", "List is empty")
            return
        flag_complete = True
        for idx_file in range(len(self.__list_full_path)) :
            if self.__list_column_integrator[idx_file].flag_executed == True : continue
            try :
                self.__list_column_integrator[idx_file].execute()
                self.list_box.itemconfig(idx_file, {"bg" : "light blue"})
                self.__list_column_integrator[idx_file].flag_executed = True
            except Exception as e :
                msg.showerror(f"{self.__list_file[idx_file]}", "Error occurred : " + str(e))
                self.list_box.itemconfig(idx_file, {"bg" : "tomato"})
                flag_complete = False
        if flag_complete == True : msg.showinfo("Info", "Integration complete")
        if self.__var_check_autoclear.get() == int(SETTING.YES) : self.__clear()

    def __show_info(self) :
        msg.showinfo("Info", MSG_INFO)

    def __event_button_enter(self, identification_option : IDENTIFICATION_OPTION) :
        match (identification_option) :
            case IDENTIFICATION_OPTION.SENSOR_ID :
                self.label_explanation.configure(text = MODULE_IDENTIFICATION_MSG.sensorid)
            case IDENTIFICATION_OPTION.BARCODE :
                self.label_explanation.configure(text = MODULE_IDENTIFICATION_MSG.barcode)
            case IDENTIFICATION_OPTION.SENSOR_ID_AND_BARCODE :
                self.label_explanation.configure(text = MODULE_IDENTIFICATION_MSG.sensorid_and_barcode)
            case IDENTIFICATION_OPTION.AUTO :
                self.label_explanation.configure(text = MODULE_IDENTIFICATION_MSG.auto)
        
    def __event_button_leave(self, event) :
        self.label_explanation.configure(text = EXPLANATION_MSG_DEFAULT)

    def run_ui(self) :

        self.__root.after(0, self.__set_window)

        self.frame_title = ck.CTkFrame(self.__root, height = 15, fg_color = "transparent")
        self.frame_title.pack(fill = "x", padx = 10, pady = 10)

        self.frame_title.bind("<ButtonPress-1>", self.__start_move_window)
        self.frame_title.bind('<B1-Motion>', self.__execute_window_movement)
        self.frame_title.bind("<ButtonRelease-1>", self.__stop_move_window)
        
        self.label_title_1 = ck.CTkLabel(self.frame_title, text = "Column", font = self.__font_title_bold)
        self.label_title_1.pack(padx = 5, pady = 10, side = "left")

        self.label_title_2 = ck.CTkLabel(self.frame_title, text = "Integrator", font = self.__font_title)
        self.label_title_2.pack(padx = 5, pady = 10, side = "left")

        self.frame_listbox = ck.CTkFrame(self.__root, fg_color = "transparent")
        self.frame_listbox.pack(fill = "x", padx = 10, pady = 10)

        self.scrollbar_listbox = ck.CTkScrollbar(self.frame_listbox)
        self.scrollbar_listbox.pack(side = "right", fill = "y")
        
        self.list_box = tk.Listbox(self.frame_listbox, selectmode = "extended", height = 10, background = "gray25", foreground = "white", font = self.__font_listbox, yscrollcommand=self.scrollbar_listbox.set)
        self.list_box.pack(side = "left", fill = "both", expand = True, padx = 10)
        self.scrollbar_listbox.configure(command = self.list_box.yview)
        self.list_box.drop_target_register(dnd.DND_FILES)
        self.list_box.dnd_bind("<<Drop>>", self.__add_listbox)
        
        self.frame_identification_button = ck.CTkFrame(self.__root)
        self.frame_identification_button.pack(fill = "x", padx = 10, pady = 10)

        self.label_identification = ck.CTkLabel(self.frame_identification_button, text = "모듈 구분 기준")
        self.radio_button_identification_1 = ck.CTkRadioButton(self.frame_identification_button, text = "센서 아이디", value = int(IDENTIFICATION_OPTION.SENSOR_ID), radiobutton_height = 17, radiobutton_width = 17, height = 25, variable = self.__var_identification)
        self.radio_button_identification_1.select()
        self.radio_button_identification_2 = ck.CTkRadioButton(self.frame_identification_button, text = "바코드", value = int(IDENTIFICATION_OPTION.BARCODE), radiobutton_height = 17, radiobutton_width = 17, height = 25, variable = self.__var_identification)
        self.radio_button_identification_3 = ck.CTkRadioButton(self.frame_identification_button, text = "센서 아이디와 바코드", value = int(IDENTIFICATION_OPTION.SENSOR_ID_AND_BARCODE), radiobutton_height = 17, radiobutton_width = 17, height = 25, variable = self.__var_identification)
        self.radio_button_identification_4 = ck.CTkRadioButton(self.frame_identification_button, text = "알아서 구분", value = int(IDENTIFICATION_OPTION.AUTO), radiobutton_height = 17, radiobutton_width = 17, height = 25, variable = self.__var_identification)

        self.label_identification.grid(column = 0, row = 0, sticky = "w")
        self.radio_button_identification_1.grid(column = 0, row = 1, sticky = "w")
        self.radio_button_identification_2.grid(column = 0, row = 2, sticky = "w")
        self.radio_button_identification_3.grid(column = 0, row = 3, sticky = "w")
        self.radio_button_identification_4.grid(column = 0, row = 4, sticky = "w")


        self.frame_duplicate_button = ck.CTkFrame(self.__root)
        self.frame_duplicate_button.pack(fill = "x", padx = 10, pady = 10)

        self.label_duplicate = ck.CTkLabel(self.frame_duplicate_button, text = "중복 제거 옵션")
        self.radio_button_duplicate_1 = ck.CTkRadioButton(self.frame_duplicate_button, text = "중복 제거 하지 않음", value = int(DUPLICATE_OPTION.DO_NOT_DROP), radiobutton_height = 17, radiobutton_width = 17, height = 25, variable = self.__var_duplicate)
        self.radio_button_duplicate_1.select()
        self.radio_button_duplicate_2 = ck.CTkRadioButton(self.frame_duplicate_button, text = "각 랏의 첫 검사만 남기고 중복 제거", value = int(DUPLICATE_OPTION.LEAVE_FIRST_FROM_EACH_LOT), radiobutton_height = 17, radiobutton_width = 17, height = 25, variable = self.__var_duplicate)
        self.radio_button_duplicate_3 = ck.CTkRadioButton(self.frame_duplicate_button, text = "각 랏의 마지막 검사만 남기고 중복 제거", value = int(DUPLICATE_OPTION.LEAVE_LAST_FROM_EACH_LOT), radiobutton_height = 17, radiobutton_width = 17, height = 25, variable = self.__var_duplicate)
        self.radio_button_duplicate_4 = ck.CTkRadioButton(self.frame_duplicate_button, text = "랏 상관 없이 시간상 첫 검사만 남기고 중복 제거", value = int(DUPLICATE_OPTION.LEAVE_FIRST_FROM_WHOLE), radiobutton_height = 17, radiobutton_width = 17, height = 25, variable = self.__var_duplicate)
        self.radio_button_duplicate_5 = ck.CTkRadioButton(self.frame_duplicate_button, text = "랏 상관 없이 시간상 마지막 검사만 남기고 중복 제거", value = int(DUPLICATE_OPTION.LEAVE_LAST_FROM_WHOLE), radiobutton_height = 17, radiobutton_width = 17, height = 25, variable = self.__var_duplicate)
        
        self.label_duplicate.grid(column = 0, row = 0, sticky = "w")
        self.radio_button_duplicate_1.grid(column = 0, row = 1, sticky = "w")
        self.radio_button_duplicate_2.grid(column = 0, row = 2, sticky = "w")
        self.radio_button_duplicate_3.grid(column = 0, row = 3, sticky = "w")
        self.radio_button_duplicate_4.grid(column = 0, row = 4, sticky = "w")
        self.radio_button_duplicate_5.grid(column = 0, row = 5, sticky = "w")

        self.frame_auto_run_clear = ck.CTkFrame(self.__root)
        self.frame_auto_run_clear.pack(fill = "x", padx = 10, pady = 10)

        self.checkbox_autorun = ck.CTkCheckBox(self.frame_auto_run_clear, text = "파일 추가 후 자동 시작", checkbox_height = 17, checkbox_width = 17, height = 25, variable = self.__var_check_autorun)
        self.checkbox_autoclear = ck.CTkCheckBox(self.frame_auto_run_clear, text = "실행 후 자동 클리어", checkbox_height = 17, checkbox_width = 17, height = 25, variable = self.__var_check_autoclear)

        self.checkbox_autorun.grid(column = 0, row = 0, sticky = "w")
        self.checkbox_autoclear.grid(column = 0, row = 1, sticky = "w")

        self.frame_btn = ck.CTkFrame(self.__root, fg_color = "transparent")
        self.frame_btn.pack(fill = "x", padx = 10, pady = 10)

        self.btn_exit = ck.CTkButton(self.frame_btn, text = "Exit", width = 10, command = self.__root.quit)
        self.btn_exit.pack(side = "right", padx = 10)
        self.btn_clear = ck.CTkButton(self.frame_btn, text = "Clear", width = 10, command = self.__clear)
        self.btn_clear.pack(side = "right", padx = 10)
        self.btn_run = ck.CTkButton(self.frame_btn, text = "Run", width = 10, command = self.__execute_integration)
        self.btn_run.pack(side = "right", padx = 10)
        self.btn_info = ck.CTkButton(self.frame_btn, text = "Info", width = 10, command = self.__show_info)
        self.btn_info.pack(side = "left", padx = 10)
        
        self.frame_explanation = ck.CTkFrame(self.__root, fg_color = "transparent")
        self.frame_explanation.pack(fill = "x", padx = 10, pady = 15)
        self.label_explanation = ck.CTkLabel(self.frame_explanation, text = EXPLANATION_MSG_DEFAULT)
        self.label_explanation.pack(fill = "x")
        self.radio_button_identification_1.bind("<Enter>", lambda x : self.__event_button_enter(IDENTIFICATION_OPTION.SENSOR_ID))
        self.radio_button_identification_1.bind("<Leave>", self.__event_button_leave)
        self.radio_button_identification_2.bind("<Enter>", lambda x : self.__event_button_enter(IDENTIFICATION_OPTION.BARCODE))
        self.radio_button_identification_2.bind("<Leave>", self.__event_button_leave)
        self.radio_button_identification_3.bind("<Enter>", lambda x : self.__event_button_enter(IDENTIFICATION_OPTION.SENSOR_ID_AND_BARCODE))
        self.radio_button_identification_3.bind("<Leave>", self.__event_button_leave)
        self.radio_button_identification_4.bind("<Enter>", lambda x : self.__event_button_enter(IDENTIFICATION_OPTION.AUTO))
        self.radio_button_identification_4.bind("<Leave>", self.__event_button_leave)

        self.__root.mainloop()


class CsvFile :
    def __init__(self, file_name, no_header=False, codec='utf-8') :
        if no_header :
            f = open(file_name, encoding=codec)
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
        self.__df_list : list[pd.DataFrame] = []
        self.__file_name = file_name
        self.__result = pd.DataFrame()
        self.codec = 'utf-8'
        self.flag_executed = False
        try :
            self.log = CsvFile(file_name, no_header=True, codec = self.codec)
        except :
            try :
                self.codec = 'cp949'
                self.log = CsvFile(file_name, no_header=True, codec = self.codec)
            except :
                self.codec = 'euc-kr'
                self.log = CsvFile(file_name, no_header=True, codec = self.codec)

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

    def __is_empty(self, row, column) -> bool :
        return self.__result.loc[row, column] == "" or self.__result.loc[row, column] == "0"

    def __make_temporary_module_id(self, sensorid_header : str, barcode_header : str) :
        self.__result["temporary_module_id"] = ""
        module_list : list[ModuleInfo] = []

        for row in range(len(self.__result)) :
            exist_temporary_module_id = False
            if self.__is_empty(row, sensorid_header) == False and exist_temporary_module_id == False :
                for module in module_list :
                    if module.sensorid != self.__result.loc[row, sensorid_header] : continue
                    exist_temporary_module_id = True
                    self.__result.loc[row, "temporary_module_id"] = str(module.temporary_module_id)
                    if self.__is_empty(row, barcode_header) == False and (module.barcode == "" or module.barcode == "0") :
                        module.barcode = self.__result.loc[row, barcode_header]
            
            if self.__is_empty(row, barcode_header) == False and exist_temporary_module_id == False :
                for module in module_list :
                    if module.barcode != self.__result.loc[row, barcode_header] : continue
                    exist_temporary_module_id = True
                    self.__result.loc[row, "temporary_module_id"] = str(module.temporary_module_id)
                    if self.__is_empty(row, sensorid_header) == False and (module.sensorid == "" or module.sensorid == "0") :
                        module.sensorid = self.__result.loc[row, sensorid_header]

            if exist_temporary_module_id == True : continue

            self.__result.loc[row, "temporary_module_id"] = str(len(module_list) + 1)
            module_list.append(ModuleInfo(sensorid = self.__result.loc[row, sensorid_header], barcode = self.__result.loc[row, barcode_header], temporary_module_id = len(module_list) + 1))

    def __make_temporary_module_id_go(self, sensorid_header : str, barcode_header : str) :
        self.__result["temporary_module_id"] = ui_mgr.dll_mgr_temporary_module_id_go.make_temporary_module_id_go(self.__result[sensorid_header].to_list(), self.__result[barcode_header].to_list())

    def remove_unexpected_columns(self) :
        for df in self.__df_list :
            if None in df.columns :
                df.drop([None], axis = 1, inplace = True)
            if "" in df.columns :
                df.drop("", axis = 1, inplace = True)

    def execute(self) :
        split_start = 0
        for row in range(1, len(self.log.data)) :
            if self.log.data.iloc[row][0] != self.log.data.iloc[0][0] : continue
            self.__df_list.append(self.log.split_csv(row_begin=split_start, row_end=row))
            split_start = row
        self.__df_list.append(self.log.split_csv(row_begin=split_start, row_end=len(self.log.data)))

        self.__df_list.sort(key=lambda x : len(x.columns), reverse=True)
        self.remove_unexpected_columns()
        self.__result = pd.concat(self.__df_list, ignore_index=True)

        sorted_headers = self.__sort_headers()
        self.__result = self.__result.reindex(columns = sorted_headers)
        
        time_header = self.__find_header(headers = sorted_headers, list_candidate = ["time", "Time", "GlobalTime"])
        lotnum_header = self.__find_header(headers = sorted_headers, list_candidate = ["lotNum", "LotNum"])
        barcode_header = self.__find_header(headers = sorted_headers, list_candidate = ["barcode", "Barcode"])
        sensorid_header = self.__find_header(headers = sorted_headers, list_candidate = ["sensorID", "SensorID"])

        if (ui_mgr.get_var_duplicate() != int(DUPLICATE_OPTION.DO_NOT_DROP)) :
            self.__result.sort_values(by = [time_header], inplace = True, ascending = True, kind = 'quicksort', ignore_index = True)

        subset_duplicate = []
        if ui_mgr.get_var_duplicate() == int(DUPLICATE_OPTION.LEAVE_FIRST_FROM_EACH_LOT) or ui_mgr.get_var_duplicate() == int(DUPLICATE_OPTION.LEAVE_LAST_FROM_EACH_LOT) :
            subset_duplicate.append(lotnum_header)
        match (ui_mgr.get_var_identification()) :
            case int(IDENTIFICATION_OPTION.SENSOR_ID) :
                subset_duplicate.append(sensorid_header)
            case int(IDENTIFICATION_OPTION.BARCODE) :
                subset_duplicate.append(barcode_header)
            case int(IDENTIFICATION_OPTION.SENSOR_ID_AND_BARCODE) :
                subset_duplicate.append(sensorid_header)
                subset_duplicate.append(barcode_header)
            case int(IDENTIFICATION_OPTION.AUTO) :
                if ui_mgr.exist_dll == True :
                    self.__make_temporary_module_id_go(sensorid_header = sensorid_header, barcode_header = barcode_header)
                else :
                    self.__make_temporary_module_id(sensorid_header = sensorid_header, barcode_header = barcode_header)
                subset_duplicate.append("temporary_module_id")

        match (ui_mgr.get_var_duplicate()) :
            case int(DUPLICATE_OPTION.DO_NOT_DROP) :
                pass
            case int(DUPLICATE_OPTION.LEAVE_FIRST_FROM_EACH_LOT) :
                self.__result.drop_duplicates(subset_duplicate, inplace = True, keep = "first", ignore_index = True)
            case int(DUPLICATE_OPTION.LEAVE_LAST_FROM_EACH_LOT) :
                self.__result.drop_duplicates(subset_duplicate, inplace = True, keep = "last", ignore_index = True)
            case int(DUPLICATE_OPTION.LEAVE_FIRST_FROM_WHOLE) :
                self.__result.drop_duplicates(subset_duplicate, inplace = True, keep = "first", ignore_index = True)
            case int(DUPLICATE_OPTION.LEAVE_LAST_FROM_WHOLE) :
                self.__result.drop_duplicates(subset_duplicate, inplace = True, keep = "last", ignore_index = True)
        
        if ui_mgr.get_var_identification() == int(IDENTIFICATION_OPTION.AUTO) :
            self.__result.drop(["temporary_module_id"], axis = 1, inplace = True)
        self.__result.to_csv(self.__file_name.replace(".csv", "_Result.csv").replace(".CSV", "_Result.csv"), index = None, encoding = self.codec)


if __name__ == "__main__" :
    ui_mgr = UiMgr()
    ui_mgr.run_ui()
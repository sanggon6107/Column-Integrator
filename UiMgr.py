from mimetypes import init
import tkinter as tk
from tkinter import messagebox as msg
import tkinterdnd2 as dnd
import customtkinter as ck
from tkinter import font
import re
from ctypes import windll

from ColumnIntegrator import *

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
        self.__var_make_comprehensive_file = tk.IntVar()

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
        if self.__var_check_autorun.get() == int(SETTING.YES) : self.__execute_integration(False)

    def __clear(self) :
        self.list_box.delete(0, tk.END)
        self.__list_full_path.clear()
        self.__list_file.clear()
        self.__list_column_integrator.clear()

    def __execute_integration(self, flag_make_comprehensive_file : bool) :
        if len(self.__list_full_path) == 0 :
            msg.showerror("Info", "List is empty")
            return
        flag_complete = True
        for idx_file in range(len(self.__list_full_path)) :
            if self.__list_column_integrator[idx_file].flag_executed == True : continue
            try :
                self.__list_column_integrator[idx_file].execute(self.exist_dll, flag_make_comprehensive_file, self.get_var_duplicate(), self.get_var_identification(), self.dll_mgr_temporary_module_id_go)
                if flag_make_comprehensive_file == False : self.__list_column_integrator[idx_file].to_csv_file
                self.__list_column_integrator[idx_file].flag_executed = True
                self.list_box.itemconfig(idx_file, {"bg" : "light blue"})
            except Exception as e :
                msg.showerror(f"{self.__list_file[idx_file]}", "Error occurred : " + str(e))
                self.list_box.itemconfig(idx_file, {"bg" : "tomato"})
                flag_complete = False

        if flag_make_comprehensive_file == True : self.__execute_integration_and_make_comprehensive_file()

        if flag_complete == True : msg.showinfo("Info", "Integration complete")
        if self.__var_check_autoclear.get() == int(SETTING.YES) : self.__clear()

    def __execute_integration_and_make_comprehensive_file(self) :
        comprehensive_data_file_maker = ComprehensiveDataFileMaker([column_integrator.get_result() for column_integrator in self.__list_column_integrator], [column_integrator.get_header("sensorid") for column_integrator in self.__list_column_integrator])
        comprehensive_data_file_maker.execute()
        comprehensive_data_file_maker.to_csv_file(self.__list_full_path[0])

    def __show_info(self) :
        msg.showinfo("Info", MSG_INFO)

    def __event_button_enter(self, type : str, option) :
        if type == "IDENTIFICATION_OPTION" :
            match (option) :
                case IDENTIFICATION_OPTION.SENSOR_ID :
                    self.label_explanation.configure(text = MSG_MODULE_IDENTIFICATION.sensorid)
                case IDENTIFICATION_OPTION.BARCODE :
                    self.label_explanation.configure(text = MSG_MODULE_IDENTIFICATION.barcode)
                case IDENTIFICATION_OPTION.SENSOR_ID_AND_BARCODE :
                    self.label_explanation.configure(text = MSG_MODULE_IDENTIFICATION.sensorid_and_barcode)
                case IDENTIFICATION_OPTION.AUTO :
                    self.label_explanation.configure(text = MSG_MODULE_IDENTIFICATION.auto)
        elif type == "BUTTON" :
            match (option) :
                case BUTTON.RUN :
                    self.label_explanation.configure(text = MSG_BUTTON.run)
                case BUTTON.INTEGRATE_ALL :
                    self.label_explanation.configure(text = MSG_BUTTON.integrate_all)
        elif type == "MAKE_COMPREHENSIVE_FILE_OPTION" :
            match (option) :
                case MAKE_COMPREHENSIVE_FILE_OPTION.DO_NOT_MAKE :
                    self.label_explanation.configure(text = MSG_MAKE_COMPREHENSIVE_FILE.do_not_make)
                case MAKE_COMPREHENSIVE_FILE_OPTION.HORIZONTAL :
                    self.label_explanation.configure(text = MSG_MAKE_COMPREHENSIVE_FILE.horizontal)
                case MAKE_COMPREHENSIVE_FILE_OPTION.VERTICAL :
                    self.label_explanation.configure(text = MSG_MAKE_COMPREHENSIVE_FILE.vertical)


    def __event_button_leave(self, event) :
        self.label_explanation.configure(text = MSG_EXPLANATION_DEFAULT)

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
        self.radio_button_identification_1.grid(column = 0, row = 1, sticky = "w", padx = 10)
        self.radio_button_identification_2.grid(column = 0, row = 2, sticky = "w", padx = 10)
        self.radio_button_identification_3.grid(column = 1, row = 1, sticky = "w", padx = 30)
        self.radio_button_identification_4.grid(column = 1, row = 2, sticky = "w", padx = 30)


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
        self.radio_button_duplicate_1.grid(column = 0, row = 1, sticky = "w", padx = 10)
        self.radio_button_duplicate_2.grid(column = 0, row = 2, sticky = "w", padx = 10)
        self.radio_button_duplicate_3.grid(column = 1, row = 1, sticky = "w", padx = 30)
        self.radio_button_duplicate_4.grid(column = 1, row = 2, sticky = "w", padx = 30)
        self.radio_button_duplicate_5.grid(column = 1, row = 3, sticky = "w", padx = 30)

        self.frame_comprehensive_file = ck.CTkFrame(self.__root)
        self.frame_comprehensive_file.pack(fill = "x", padx = 10, pady = 10)

        self.label_make_comprehensive_file = ck.CTkLabel(self.frame_comprehensive_file, text = "파일 통합 옵션")
        self.radio_button_make_comprehensive_file_1 = ck.CTkRadioButton(self.frame_comprehensive_file, text = "통합하지 않음", value = int(MAKE_COMPREHENSIVE_FILE_OPTION.DO_NOT_MAKE), radiobutton_height = 17, radiobutton_width = 17, height = 25, variable = self.__var_make_comprehensive_file)
        self.radio_button_make_comprehensive_file_1.select()
        self.radio_button_make_comprehensive_file_2 = ck.CTkRadioButton(self.frame_comprehensive_file, text = "가로로 통합", value = int(MAKE_COMPREHENSIVE_FILE_OPTION.HORIZONTAL), radiobutton_height = 17, radiobutton_width = 17, height = 25, variable = self.__var_make_comprehensive_file)
        self.radio_button_make_comprehensive_file_3 = ck.CTkRadioButton(self.frame_comprehensive_file, text = "세로로 통합", value = int(MAKE_COMPREHENSIVE_FILE_OPTION.VERTICAL), radiobutton_height = 17, radiobutton_width = 17, height = 25, variable = self.__var_make_comprehensive_file)

        self.label_make_comprehensive_file.grid(column = 0, row = 0, sticky = "w")
        self.radio_button_make_comprehensive_file_1.grid(column = 0, row = 1, sticky = "w", padx = 10)
        self.radio_button_make_comprehensive_file_2.grid(column = 0, row = 2, sticky = "w", padx = 10)
        self.radio_button_make_comprehensive_file_3.grid(column = 0, row = 3, sticky = "w", padx = 10)

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
        self.btn_run = ck.CTkButton(self.frame_btn, text = "Run", width = 10, command = lambda : self.__execute_integration(False))
        self.btn_run.pack(side = "right", padx = 10)
        self.btn_integrate_all = ck.CTkButton(self.frame_btn, text = "리스트 내 파일을 하나로 통합", command = lambda : self.__execute_integration(True))
        self.btn_integrate_all.pack(side = "right", padx = 20)
        self.btn_info = ck.CTkButton(self.frame_btn, text = "Info", width = 10, command = self.__show_info)
        self.btn_info.pack(side = "left", padx = 10)
        
        self.frame_explanation = ck.CTkFrame(self.__root, fg_color = "transparent")
        self.frame_explanation.pack(fill = "x", padx = 10, pady = 15)
        self.label_explanation = ck.CTkLabel(self.frame_explanation, text = MSG_EXPLANATION_DEFAULT)
        self.label_explanation.pack(fill = "x")
        self.radio_button_identification_1.bind("<Enter>", lambda x : self.__event_button_enter("IDENTIFICATION_OPTION", IDENTIFICATION_OPTION.SENSOR_ID))
        self.radio_button_identification_1.bind("<Leave>", self.__event_button_leave)
        self.radio_button_identification_2.bind("<Enter>", lambda x : self.__event_button_enter("IDENTIFICATION_OPTION", IDENTIFICATION_OPTION.BARCODE))
        self.radio_button_identification_2.bind("<Leave>", self.__event_button_leave)
        self.radio_button_identification_3.bind("<Enter>", lambda x : self.__event_button_enter("IDENTIFICATION_OPTION", IDENTIFICATION_OPTION.SENSOR_ID_AND_BARCODE))
        self.radio_button_identification_3.bind("<Leave>", self.__event_button_leave)
        self.radio_button_identification_4.bind("<Enter>", lambda x : self.__event_button_enter("IDENTIFICATION_OPTION", IDENTIFICATION_OPTION.AUTO))
        self.radio_button_identification_4.bind("<Leave>", self.__event_button_leave)
        self.btn_run.bind("<Enter>", lambda x : self.__event_button_enter("BUTTON", BUTTON.RUN))
        self.btn_run.bind("<Leave>", self.__event_button_leave)
        self.btn_integrate_all.bind("<Enter>", lambda x : self.__event_button_enter("BUTTON", BUTTON.INTEGRATE_ALL))
        self.btn_integrate_all.bind("<Leave>", self.__event_button_leave)
        self.radio_button_make_comprehensive_file_2.bind("<Enter>", lambda x : self.__event_button_enter("MAKE_COMPREHENSIVE_FILE_OPTION", MAKE_COMPREHENSIVE_FILE_OPTION.HORIZONTAL))
        self.radio_button_make_comprehensive_file_2.bind("<Leave>", self.__event_button_leave)
        self.radio_button_make_comprehensive_file_3.bind("<Enter>", lambda x : self.__event_button_enter("MAKE_COMPREHENSIVE_FILE_OPTION", MAKE_COMPREHENSIVE_FILE_OPTION.VERTICAL))
        self.radio_button_make_comprehensive_file_3.bind("<Leave>", self.__event_button_leave)

        self.__root.mainloop()

if __name__ == "__main__" :
    ui_mgr = UiMgr()
    ui_mgr.run_ui()
from DllMgrTemporaryModuleId import *
from GlobalVariables import *

import pandas as pd
import csv
import copy

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
        self.__dict_headers : dict[str, str] = {}

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

    def get_result(self) -> pd.DataFrame :
        return self.__result
    
    def get_header(self, key : str) -> str :
        return self.__dict_headers[key]

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

    def __make_temporary_module_id_go(self, sensorid_header : str, barcode_header : str, dll_mgr_temporary_module_id_go : DllMgrTemporaryModuleId) :
        self.__result["temporary_module_id"] = dll_mgr_temporary_module_id_go.make_temporary_module_id_go(self.__result[sensorid_header].to_list(), self.__result[barcode_header].to_list())

    def remove_unexpected_columns(self) :
        for df in self.__df_list :
            if None in df.columns :
                df.drop([None], axis = 1, inplace = True)
            if "" in df.columns :
                df.drop("", axis = 1, inplace = True)

    def to_csv_file(self) :
        self.__result.to_csv(self.__file_name.replace(".csv", "_Result.csv").replace(".CSV", "_Result.csv"), index = None, encoding = self.codec)

    def execute(self, flag_dll_exist : bool, flag_make_comprehensive_file : bool, var_duplicate : int, var_identification : int, dll_mgr_temporary_module_id_go : DllMgrTemporaryModuleId) :
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
        
        self.__dict_headers["time"] = self.__find_header(headers = sorted_headers, list_candidate = ["time", "Time", "GlobalTime"])
        self.__dict_headers["lotnum"] = self.__find_header(headers = sorted_headers, list_candidate = ["lotNum", "LotNum"])
        self.__dict_headers["barcode"] = self.__find_header(headers = sorted_headers, list_candidate = ["barcode", "Barcode"])
        self.__dict_headers["sensorid"] = self.__find_header(headers = sorted_headers, list_candidate = ["sensorID", "SensorID"])

        if flag_make_comprehensive_file == True :
            var_identification = int(IDENTIFICATION_OPTION.SENSOR_ID)
            var_duplicate = int(DUPLICATE_OPTION.LEAVE_LAST_FROM_WHOLE)

        if (var_duplicate != int(DUPLICATE_OPTION.DO_NOT_DROP)) :
            self.__result.sort_values(by = [self.__dict_headers["time"]], inplace = True, ascending = True, kind = 'quicksort', ignore_index = True)
        subset_duplicate = []
        if var_duplicate == int(DUPLICATE_OPTION.LEAVE_FIRST_FROM_EACH_LOT) or var_duplicate == int(DUPLICATE_OPTION.LEAVE_LAST_FROM_EACH_LOT) :
            subset_duplicate.append(self.__dict_headers["lotnum"])
        match (var_identification) :
            case int(IDENTIFICATION_OPTION.SENSOR_ID) :
                subset_duplicate.append(self.__dict_headers["sensorid"])
            case int(IDENTIFICATION_OPTION.BARCODE) :
                subset_duplicate.append(self.__dict_headers["barcode"])
            case int(IDENTIFICATION_OPTION.SENSOR_ID_AND_BARCODE) :
                subset_duplicate.append(self.__dict_headers["sensorid"])
                subset_duplicate.append(self.__dict_headers["barcode"])
            case int(IDENTIFICATION_OPTION.AUTO) :
                if flag_dll_exist == True :
                    self.__make_temporary_module_id_go(sensorid_header = self.__dict_headers["sensorid"], barcode_header = self.__dict_headers["barcode"], dll_mgr_temporary_module_id_go = dll_mgr_temporary_module_id_go)
                else :
                    self.__make_temporary_module_id(sensorid_header = self.__dict_headers["sensorid"], barcode_header = self.__dict_headers["barcode"])
                subset_duplicate.append("temporary_module_id")

        match (var_duplicate) :
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
        
        if var_identification == int(IDENTIFICATION_OPTION.AUTO) :
            self.__result.drop(["temporary_module_id"], axis = 1, inplace = True)
        
        self.to_csv_file()


class ComprehensiveDataFileMaker :
    def __init__(self, list_df : list[pd.DataFrame], list_sensorid : list[str]) :
        self.__list_df = copy.deepcopy(list_df)
        self.__list_sensorid = [list_sensorid[idx_list] + f"ColIntSuf{idx_list}" for idx_list in range(0, len(list_sensorid))]

        for idx_df in range(0, len(list_df)) :
            self.__list_df[idx_df].rename(columns = {list_sensorid[idx_df] : self.__list_sensorid[idx_df]}, inplace = True)
        
        self.__result : pd.DataFrame = self.__list_df[0]

    def execute(self) :
        for idx_df in range(1, len(self.__list_df)) : 

            self.__result = pd.merge(self.__result, self.__list_df[idx_df], how = "outer", left_on = self.__list_sensorid[0], right_on = self.__list_sensorid[idx_df], suffixes=["ColIntSufL", "ColIntSufR"])

        self.__result.columns = [header.split("ColIntSuf")[0] for header in self.__result.columns]

    def to_csv_file(self, file_name : str) :
        self.__result.to_csv(file_name.replace(".csv", "_MergedLog.csv").replace(".CSV", "_MergedLog.csv"), index = None)
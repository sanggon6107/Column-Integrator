from DllMgrTemporaryModuleId import *
from GlobalVariables import *
from CpplishLogger import *

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
        LOG(logging.DEBUG) << f"CsvFile instantiated. codec : {codec}"

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
        LOG(logging.DEBUG) << f"Function call : CsvFile.split_csv. row_begin : {row_begin}, row_end : {row_end}"
        ret_temp = self.data.iloc[row_begin:row_end,:]
        ret_temp.rename(columns=ret_temp.iloc[0], inplace=True)
        ret_temp.drop(ret_temp.index[0], inplace=True)
        ret_temp.reset_index(drop = True, inplace = True)
        ret_temp.dropna(how='all', axis='columns', inplace=True)

        LOG(logging.DEBUG) << f"split_csv complete. ret_temp shape : {ret_temp.shape}"
        return ret_temp


class ColumnIntegrator :
    def __init__(self, file_name : str, df_list : list[pd.DataFrame], codec : str = 'utf-8') :
        LOG(logging.DEBUG) << "ColumnIntegrator instantiated"
        self.__df_list : list[pd.DataFrame] = df_list
        self.__file_name = file_name
        self.__result = pd.DataFrame()
        self.codec = codec
        self.__flag_executed = False
        self.__dict_headers : dict[str, str] = {}

        self.remove_unexpected_columns()
        
        # DEPRECATED : The below works are conducted via init_df and init_file

        # try :
        #     self.log = CsvFile(file_name, no_header=True, codec = self.codec)
        # except :
        #     try :
        #         self.codec = 'cp949'
        #         self.log = CsvFile(file_name, no_header=True, codec = self.codec)
        #     except :
        #         self.codec = 'euc-kr'
        #         self.log = CsvFile(file_name, no_header=True, codec = self.codec)

    # This constructor must receive preprocessed dataframes.
    @classmethod
    def init_df(cls, file_name : str, list_df : list[pd.DataFrame]) -> 'ColumnIntegrator' :
        '''
        Constructor that initialize a ColumnIntegrator using filename and a list of DataFrame.
        Every DataFrame passed to this constructor must be already column-integrated.
        
        :param file_name: Represents Dataframe. This param needs to decide the path to export the result Dataframe as a csv file.
        :param list_df: A list that consists of DataFrames. ColumnIntegrator will eventually integrate these Dataframe into a single Dataframe. 
        :return: This function will finally intialize and return a ColumIntegrator instance that contains has tables to integrate.
        '''
        LOG(logging.DEBUG) << "Function call : ColumnIntegrator.init_df"
        return cls(file_name, list_df)
    
    @classmethod
    def init_file(cls, file_name : str) -> 'ColumnIntegrator' :
        '''
        Consturctor that initialize a ColumnIntegrator using a file name. This constructor is used to initialize the ColumnIntegrator using a csv file
        that has many different vertically, and successively logged tables.
        This function splits the tables into different DataFrames and initialize a ColumnIntegrator instance.

        :param file_name: The name of the csv file to load.
        :return: This function will finally intialize and return a ColumIntegrator instance that contains has tables to integrate.
        '''
        LOG(logging.DEBUG) << "Function call : ColumnIntegrator.init_file"
        codec = 'utf-8'
        try :
            log = CsvFile(file_name, no_header=True, codec = codec)
        except :
            try :
                codec = 'cp949'
                log = CsvFile(file_name, no_header=True, codec = codec)
            except :
                codec = 'euc-kr'
                log = CsvFile(file_name, no_header=True, codec = codec)
        LOG(logging.DEBUG) << f"Codec : {codec}"

        LOG(logging.DEBUG) << "Split the csv file into tables with a single set of headers on top."
        split_start = 0
        df_list : list[pd.DataFrame] = []
        for row in range(1, len(log.data)) :
            if log.data.iloc[row][0] != log.data.iloc[0][0] : continue
            LOG(logging.DEBUG) << f"Confronted with the column row : {log.data.iloc[row][0]} == {log.data.iloc[0][0]}"
            df_list.append(log.split_csv(row_begin=split_start, row_end=row))
            LOG(logging.DEBUG) << f"split_start updated : {row}"
            split_start = row
        df_list.append(log.split_csv(row_begin=split_start, row_end=len(log.data)))
        df_list.sort(key=lambda x : len(x.columns), reverse=True)
        
        return cls(file_name, df_list, codec = codec)

    def __sort_headers(self) -> pd.DataFrame :
        LOG(logging.DEBUG) << "sort headers"
        headers_list = []
        for df in self.__df_list :
            headers_list.append(list(df.columns))

        result = list(copy.deepcopy(headers_list[0]))
        for header in headers_list :
            for idx in range(0, len(header)) :
                if header[idx] in result :
                    LOG(logging.DEBUG) << f"Header already exists : {header[idx]}"
                    continue
                LOG(logging.DEBUG) << f"insert the added header : {header[idx]}"
                result.insert(result.index(header[idx - 1]) + 1, header[idx])

        return result

    def __find_header(self, headers : list, list_candidate : list) -> str :
        LOG(logging.DEBUG) << "Function call : ColumnIntegrator.__find_header"
        for candidate in list_candidate :
            if not candidate in headers :
                LOG(logging.DEBUG) << f"header candidate : {candidate}"
                continue
            LOG(logging.DEBUG) << f"Found header : {candidate}"
            return candidate
        LOG(logging.DEBUG) << "There is no suitable header expected."
        return list_candidate[-1]

    def __is_empty(self, row, column) -> bool :
        return self.__result.loc[row, column] == "" or self.__result.loc[row, column] == "0"

    def get_result(self) -> pd.DataFrame :
        return self.__result
    
    def get_header(self, key : str) -> str :
        return self.__dict_headers[key]

    def get_flag_excuted(self) -> bool :
        return self.__flag_executed
    
    def set_flag_excuted(self, arg : bool) :
        self.__flag_executed = arg
    
    def get_file_name(self) -> str :
        return self.__file_name.split("/")[-1]

    def __make_temporary_module_id(self, sensorid_header : str, barcode_header : str) :
        '''
        This function will make temporary module id to identify modules that may have sensor id and module barcode.
        This function works completely the same as "MakeTemporaryModuleIdGo" which is implemented in golang.
        The software prefers golang version, but will call this function when there's no "MakeTemporaryModuleIdGo.dll" in the same path.

        :param sensorid_header: Column name that indicates sensor id. this is necessary since the sensor id header varies depending on the factory.
        :param barcode_header: Column name that indicates module barcode. this is necessary since the barcode header varies depending on the factory

        '''
        LOG(logging.DEBUG) << "Function call : ColumnIntegrator.__make_temporary_module_id"
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
        LOG(logging.DEBUG) << "Function call : ColumnIntegrator.__make_temporary_module_id_go"
        LOG(logging.DEBUG) << f"Sensor id header : {sensorid_header}, Barcode id header : {barcode_header}"
        LOG(logging.DEBUG) << f"Sensor id size : {len(self.__result[sensorid_header])}, Barcode id size : {len(self.__result[barcode_header])}"
        self.__result["temporary_module_id"] = dll_mgr_temporary_module_id_go.make_temporary_module_id_go(self.__result[sensorid_header].to_list(), self.__result[barcode_header].to_list())

    def remove_unexpected_columns(self) :
        LOG(logging.DEBUG) << "Remove all the unexpected columns that have void name to avoid exception occured at drop_duplicates"
        for df in self.__df_list :
            if None in df.columns :
                df.drop([None], axis = 1, inplace = True)
            if "" in df.columns :
                df.drop("", axis = 1, inplace = True)

    def remove_empty_rows(self) :
        LOG(logging.DEBUG) << "Remove all the empty rows"
        for df in self.__df_list :
            df.dropna(how = 'all', inplace = True)

    def to_csv_file(self) :
        file_name_temp = self.__file_name.replace(".csv", "_Result.csv").replace(".CSV", "_Result.csv")
        LOG(logging.DEBUG) << "Function call : ColumnIntegrator.to_csv_file."
        LOG(logging.DEBUG) << f"File exported : {file_name_temp}"
        self.__result.to_csv(file_name_temp, index = None, encoding = self.codec)

    def execute(self, flag_dll_exist : bool, flag_make_comprehensive_file_horizontal : bool, var_duplicate : int, var_identification : int, dll_mgr_temporary_module_id_go : DllMgrTemporaryModuleId) :
        '''
        1. Call the function pd.concat and integrate all the tables in vertical way.
        2. Re-order unexpectedly confused headers due to the function call(pd.caoncat).
        3. Drop duplicates and sort the data.
        
        : param flag_dll_exist: Defined when the UiMgr instance is initiated.
        : param flag_make_comprehensive_file_horizontal: A flag indicating whether the UiMgr will make an single csv file that has all the tables on the listbox integrated.
        : param var_duplicate: Option used to determine the way to drop duplicates.
        : param var_identification: Module identification option (Module id, Sensor id, Use both Module id and Sensor id, Make temporary module id )
        : param dll_mgr_temporary_module_id_go: DllMgrTemporaryModuleId instance. This will be used when 'flag_dll_exist' is True.
        '''
        # DEPRECATED : The blow feature will be conducted in consturctor (init_file).

        # split_start = 0
        # for row in range(1, len(self.log.data)) :
        #     if self.log.data.iloc[row][0] != self.log.data.iloc[0][0] : continue
        #     self.__df_list.append(self.log.split_csv(row_begin=split_start, row_end=row))
        #     split_start = row
        # self.__df_list.append(self.log.split_csv(row_begin=split_start, row_end=len(self.log.data)))
        # self.__df_list.sort(key=lambda x : len(x.columns), reverse=True)
        # self.remove_unexpected_columns()
        LOG(logging.DEBUG) << "Function call : pd.concat"
        LOG(logging.DEBUG) << f"self.__df_list size : {len(self.__df_list)}"
        self.__result = pd.concat(self.__df_list, ignore_index=True)

        sorted_headers = self.__sort_headers()
        LOG(logging.DEBUG) << "pd.reindex using sorted headers"
        self.__result = self.__result.reindex(columns = sorted_headers)
        
        LOG(logging.DEBUG) << "Find the headers that indicate time, lotnum, barcode, sensorid"
        self.__dict_headers["time"] = self.__find_header(headers = sorted_headers, list_candidate = ["time", "Time", "GlobalTime"])
        self.__dict_headers["lotnum"] = self.__find_header(headers = sorted_headers, list_candidate = ["lotNum", "LotNum"])
        self.__dict_headers["barcode"] = self.__find_header(headers = sorted_headers, list_candidate = ["barcode", "Barcode"])
        self.__dict_headers["sensorid"] = self.__find_header(headers = sorted_headers, list_candidate = ["sensorID", "SensorID"])

        LOG(logging.DEBUG) << "Check Duplicate/Identification flags"
        if flag_make_comprehensive_file_horizontal == True :
            var_identification = int(IDENTIFICATION_OPTION.SENSOR_ID)
            var_duplicate = int(DUPLICATE_OPTION.LEAVE_LAST_FROM_WHOLE)

        if (var_duplicate != int(DUPLICATE_OPTION.DO_NOT_DROP)) :
            self.__result.sort_values(by = [self.__dict_headers["time"]], inplace = True, ascending = True, kind = 'quicksort', ignore_index = True)
        subset_duplicate = []
        if var_duplicate == int(DUPLICATE_OPTION.LEAVE_FIRST_FROM_EACH_LOT) or var_duplicate == int(DUPLICATE_OPTION.LEAVE_LAST_FROM_EACH_LOT) :
            subset_duplicate.append(self.__dict_headers["lotnum"])
        match (var_identification) :
            case int(IDENTIFICATION_OPTION.SENSOR_ID) :
                LOG(logging.DEBUG) << "IDENTIFICATION_OPTION.SENSOR_ID selected"
                subset_duplicate.append(self.__dict_headers["sensorid"])
            case int(IDENTIFICATION_OPTION.BARCODE) :
                LOG(logging.DEBUG) << "IDENTIFICATION_OPTION.BARCODE selected"
                subset_duplicate.append(self.__dict_headers["barcode"])
            case int(IDENTIFICATION_OPTION.SENSOR_ID_AND_BARCODE) :
                LOG(logging.DEBUG) << "IDENTIFICATION_OPTION.SENSOR_ID_AND_BARCODE selected"
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
                LOG(logging.DEBUG) << "DUPLICATE_OPTION.LEAVE_FIRST_FROM_EACH_LOT selected"
                self.__result.drop_duplicates(subset_duplicate, inplace = True, keep = "first", ignore_index = True)
            case int(DUPLICATE_OPTION.LEAVE_LAST_FROM_EACH_LOT) :
                LOG(logging.DEBUG) << "DUPLICATE_OPTION.LEAVE_LAST_FROM_EACH_LOT selected"
                self.__result.drop_duplicates(subset_duplicate, inplace = True, keep = "last", ignore_index = True)
            case int(DUPLICATE_OPTION.LEAVE_FIRST_FROM_WHOLE) :
                LOG(logging.DEBUG) << "DUPLICATE_OPTION.LEAVE_FIRST_FROM_WHOLE selected"
                self.__result.drop_duplicates(subset_duplicate, inplace = True, keep = "first", ignore_index = True)
            case int(DUPLICATE_OPTION.LEAVE_LAST_FROM_WHOLE) :
                LOG(logging.DEBUG) << "DUPLICATE_OPTION.LEAVE_LAST_FROM_WHOLE selected"
                self.__result.drop_duplicates(subset_duplicate, inplace = True, keep = "last", ignore_index = True)
        
        if var_identification == int(IDENTIFICATION_OPTION.AUTO) :
            LOG(logging.DEBUG) << "drop temporary_module_id column after drop_duplicates"
            self.__result.drop(["temporary_module_id"], axis = 1, inplace = True)
        
        # self.to_csv_file()


class IComprehensiveDataFileMaker :
    def __init__(self, merge_type : MAKE_COMPREHENSIVE_FILE_OPTION, list_df : list[pd.DataFrame]) :
        '''
        This class and its children classes integrates multiple files into a single csv file.
        '''
        self._list_df = copy.deepcopy(list_df)
        
        self._result : pd.DataFrame = pd.DataFrame()

        self.__post_fix_merged_log : MAKE_COMPREHENSIVE_FILE_OPTION
        match (merge_type) :
            case MAKE_COMPREHENSIVE_FILE_OPTION.HORIZONTAL :
                self.__post_fix_merged_log = "Horizontal"
            case MAKE_COMPREHENSIVE_FILE_OPTION.VERTICAL :
                self.__post_fix_merged_log = "Vertical"


    def to_csv_file(self, file_name : str) :
        file_name_temp = file_name.replace(".csv", f"_MergedLog{self.__post_fix_merged_log}.csv").replace(".CSV", f"_MergedLog{self.__post_fix_merged_log}.csv")
        LOG(logging.DEBUG) << f"to_csv_file : {file_name_temp}"
        self._result.to_csv(file_name_temp, index = None, encoding='utf-8-sig')

class ComprehensiveDataFileMakerHorizontal(IComprehensiveDataFileMaker) :
    def __init__(self, merge_type : MAKE_COMPREHENSIVE_FILE_OPTION, list_sensorid : list[str], list_df : list[pd.DataFrame]) :
        '''
        This class integrates the integrated result exported by ColumnIntegrator in horizontal way.
        This class executes the integration using pd.merge(outer) to integrate the tables.
        Headers will have temporary postfix to avoid unexpected duplicates drop.

        '''
        super().__init__(merge_type, list_df)
        LOG(logging.DEBUG) << "ComprehensiveDataFileMakerHorizontal initiated"
        
        self.__list_sensorid = [list_sensorid[idx_list] + f"ColIntSuf{idx_list}" for idx_list in range(0, len(list_sensorid))]

        for idx_df in range(0, len(self._list_df)) :
            self._list_df[idx_df].rename(columns = {list_sensorid[idx_df] : self.__list_sensorid[idx_df]}, inplace = True)

    def execute(self) :
        LOG(logging.DEBUG) << "Start to integrate all the tables in the listbox"
        self._result = self._list_df[0]

        for idx_df in range(1, len(self._list_df)) : 
            self._result = pd.merge(self._result, self._list_df[idx_df], how = "outer", left_on = self.__list_sensorid[0], right_on = self.__list_sensorid[idx_df], suffixes=["ColIntSufL", "ColIntSufR"])

        self._result.columns = [header.split("ColIntSuf")[0] for header in self._result.columns]


class ComprehensiveDataFileMakerVertical(IComprehensiveDataFileMaker) :
    def __init__(self, merge_type : MAKE_COMPREHENSIVE_FILE_OPTION, file_name : str, list_df : list[pd.DataFrame]) :
        '''
        This class integrates the integrated result exported by ColumnIntegrator in vertical way.
        This class simply initializes and executes the integration using ColumnIntegrator instance.

        :param merge_type: this parameter needs to decide the posfix of the result file.
        :param file_name: this parameter needs to decide the name of the result file.
        :param list_df: ComprehensiveDataFileMakerVertical will eventually integrate these DataFrames into a single table.
        '''
        super().__init__(merge_type, list_df)
        LOG(logging.DEBUG) << "ComprehensiveDataFileMakerVertical initiated"

        self.__column_integrator : ColumnIntegrator = ColumnIntegrator.init_df(file_name, self._list_df)

    def execute(self, flag_dll_exist : bool, flag_make_comprehensive_file_horizontal : bool, var_duplicate : int, var_identification : int, dll_mgr_temporary_module_id_go : DllMgrTemporaryModuleId) :
        LOG(logging.DEBUG) << "Start to integrate all the tables in the listbox in vertical way"
        self.__column_integrator.execute(flag_dll_exist, flag_make_comprehensive_file_horizontal, var_duplicate, var_identification, dll_mgr_temporary_module_id_go)
        self._result = self.__column_integrator.get_result()
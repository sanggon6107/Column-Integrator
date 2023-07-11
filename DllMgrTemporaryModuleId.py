from ctypes import *
from numpy.ctypeslib import ndpointer

class GoSlice(Structure):
    _fields_ = [("data", POINTER(c_void_p)), 
                ("len", c_longlong), ("cap", c_longlong)]
    
class GoString(Structure):
    _fields_ = [("p", c_char_p), ("n", c_longlong)]

class DllMgr() :
    def __init__(self, path_dll_file : str) :
        self._dll = WinDLL(path_dll_file)
    def _run_dll(self, func_name, *args) :
        self.dll.func_name(*args)

class DllMgrTemporaryModuleId(DllMgr) :
    def __init__(self, path_dll_file : str) :
        super().__init__(path_dll_file)

    def make_temporary_module_id_go(self, list_sensorid, list_barcode) -> list :
        list_c_void_p_sensorid = [cast(c_char_p(str(s).encode('utf-8')),c_void_p) for s in list_sensorid]
        array_c_void_p_sensorid = (c_void_p * len(list_c_void_p_sensorid))(*list_c_void_p_sensorid)
        go_slice_sensor_id = GoSlice(array_c_void_p_sensorid,len(array_c_void_p_sensorid),len(array_c_void_p_sensorid))
        
        list_c_void_p_barcode = [cast(c_char_p(str(s).encode('utf-8')),c_void_p) for s in list_barcode]
        array_c_void_barcode = (c_void_p * len(list_c_void_p_barcode))(*list_c_void_p_barcode)
        go_slice_barcode = GoSlice(array_c_void_barcode,len(array_c_void_barcode),len(array_c_void_barcode))

        self._dll.MakeTemporaryModuleIdGo.restype = ndpointer(dtype = c_int64, shape = (len(list_sensorid),))

        return self._dll.MakeTemporaryModuleIdGo(go_slice_sensor_id, go_slice_barcode)
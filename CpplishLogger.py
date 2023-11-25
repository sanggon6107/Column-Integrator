import logging
import ctypes
from Singleton import *

OutputDebugString = ctypes.windll.kernel32.OutputDebugStringW

class DbgViewHandler(logging.Handler) :
    def emit(self, record) :
        OutputDebugString(self.format(record))


class LogMgr(metaclass=Singleton) :
    def __init__(self) :
        self.__log = logging.getLogger("output.debug.string.logger")
        self.__ods = DbgViewHandler()

        self.__fmt = logging.Formatter(fmt='%(asctime)s.%(msecs)03d [%(thread)5s] %(levelname)-8s %(funcName)-20s %(lineno)d %(message)s', datefmt='%Y:%m:%d %H:%M:%S')
        self.__log.setLevel(logging.DEBUG)

        self.__ods.setLevel(logging.DEBUG)
        self.__ods.setFormatter(self.__fmt)
        self.__log.addHandler(self.__ods)

    def log(self, level, arg : str) :
        match(level) : 
            case logging.DEBUG :
                self.__log.debug(arg)
            case logging.INFO :
                self.__log.info(arg)
            case logging.WARN :
                self.__log.warn(arg)
            case logging.ERROR :
                self.__log.error(arg)
            case logging.FATAL :
                self.__log.fatal(arg)
            case _ :
                pass
LOG_MGR = LogMgr()

class LOG :
    def __init__(self, level) :
        '''
        Cpp-lish logger.
        Level : logging.DEBUG, logging.INFO, logging.WARN, logging.ERROR, logging.FATAL
        
        : param  level: logging level
        '''
        self.__level = level

    def __lshift__(self, arg : str) :
        LOG_MGR.log(self.__level, arg)
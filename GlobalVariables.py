from enum import auto, IntEnum
from dataclasses import dataclass

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

class BUTTON(EnumFromZero) :
    RUN = auto()
    INTEGRATE_ALL = auto()

class MAKE_COMPREHENSIVE_FILE_OPTION(EnumFromZero) :
    DO_NOT_MAKE = auto()
    HORIZONTAL = auto()
    VERTICAL = auto()

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

@dataclass
class ButtonInfo :
    run : str = None
    integrate_all : str = None

@dataclass
class MakeComprehensiveFileInfo :
    do_not_make : str = None
    horizontal : str = None
    vertical : str = None

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

MSG_EXPLANATION_DEFAULT = "파일을 드래그하여 리스트에 추가할 수 있습니다. csv 확장자가 아닌 파일은 추가할 수 없습니다."

MSG_MODULE_IDENTIFICATION = ModuleIdentificationInfo(
    sensorid = "센서 아이디를 기준으로 모듈을 구분합니다.",
    barcode = "바코드를 기준으로 모듈을 구분합니다.", 
    sensorid_and_barcode = """센서 아이디와 바코드가 모두 같아야 동일 모듈로 구분합니다.
    OS Test 불량 등으로 인해 센서아이디가 0으로 기재되는 경우
    다른 테스트 데이터와 동일 모듈로 인식하지 못할 수 있습니다.""", 
    auto = """프로그램 내부 알고리즘을 사용합니다.
    센서 아이디와 바코드 중 하나가 적혀있지 않더라도 다른 데이터와 비교 및 추정하여
    동일 모듈을 식별할 수 있습니다."""
)

MSG_BUTTON = ButtonInfo(
    run = """리스트에 있는 각 파일의 컬럼을 통합합니다.
    결과는 각 파일의 경로에 생성됩니다.""", 
    integrate_all = """컬럼을 통합하고 리스트에 있는 파일을 하나로 합칩니다.
    센서 기준으로 랏 구분 없이 마지막 데이터만 남깁니다.
    결과는 리스트상 첫번째 파일의 경로에 생성됩니다."""
)

MSG_MAKE_COMPREHENSIVE_FILE = MakeComprehensiveFileInfo(
    do_not_make = "",
    horizontal = """다수의 파일을 가로로 통합합니다.
    결과는 각 파일의 첫 경로에 생성됩니다.""",
    vertical = """다수의 파일을 세로로 통합합니다.
    결과는 각 파일의 첫 경로에 생성됩니다."""
)
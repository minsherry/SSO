from enum import Enum

class ErrorNameEnum(Enum):
    '''
    用來記錄錯誤名稱 和 預設次數
    '''
    
    AUTO_LOCK = 3
    AUTO_BAN = 12
    CANNOT_USE = 15
    DEFAULT = -1
from enum import Enum

class ErrorNameEnum(Enum):
    '''
    用來記錄錯誤名稱 和 預設次數
    '''

    CANNOT_USE = 15
    AUTO_BAN = 12
    AUTO_LOCK = 3
    DEFAULT = -1

    def get_hint(self):
        return {
            'CANNOT_USE': "錯誤次數已達上限, 該帳號無法使用",
            'AUTO_BAN': "錯誤次數太多, 該帳號已禁止使用",
            'AUTO_LOCK': "錯誤次數達一定次數, 該帳號已鎖定, 請洽客服中心解鎖"
        }.get(self.name, "登入失敗")
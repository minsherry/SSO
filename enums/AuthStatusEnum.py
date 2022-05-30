from enum import Enum,unique    

@unique
class CodeNMsgEnum(Enum):
    '''
    用來記錄狀態代碼 和 回傳訊息
    '''

    DATA_FORMAT_ERROR = (1, "資料格式錯誤")

    USER_AUTH_FAIL = (10, "用戶資料驗證錯誤")
    USER_AUTH_SUCCESS = (20, "用戶資料驗證成功")

    LOGIN_LOCK = (30, "密碼錯誤超過一定次數，已上鎖")
    LOGIN_BAN =  (31, "密碼錯誤超過一定次數，已禁止")    
    LOGIN_FAIL = (32, "登入失敗，輸入資料有誤")
    LOGIN_DATA_FORMAT_ERROR = (33, "帳號密碼輸入錯誤!")
    LOGIN_SUCCESS = (34, "登入成功!")
    LOGIN_CANNNOT_USE = (39, "已達錯誤次數上限,該帳號無法使用")
    
    SIGN_UP_SUCCESS = (40, "會員註冊成功!")
    SIGN_UP_DATA_FORMAT_ERROR = (41, "會員註冊輸入資料格式錯誤!")

    USER_IS_NON_UNLOCK = (50, "用戶非鎖定狀態, 無須解鎖")
    USER_UNLOCK_SUCCESS = (51, "用戶解鎖成功")

    RETURN_USER_ACCOUNT_DATA = (60, "回傳用戶開戶資料")
    RETURN_USER_ACCOUNT_NAME = (61, "回傳用戶帳號")

    SERVICE_NOT_EXISTED = (70, "目前沒有提供該服務")

    CUSTOMIZE = (80, "自定義訊息")
        
    def __new__(cls, value, message):
        obj = object.__new__(cls)
        obj._value_ = value   # 設定這個為該Enum實體物件的value
        obj.code = value      # 新增實體屬性 code
        obj.message = message # 新增實體屬性 message
        
        return obj
    
    def get_dict(self, data = None , extra_msg = None):   
        if extra_msg:
            message = extra_msg
        else:
            message = self.message

        result = {
            "code": self.code,
            "message": message,
            "data": data
        }

        return result
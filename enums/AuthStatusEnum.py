from enum import Enum

class CodeMessageEnum(Enum):  
     

    USER_AUTH_FAIL =  10
    USER_AUTH_SUCCESS = 20

    CODE_MESSAGE =  {
                    "10":{"code": 10, "message": "用戶資料驗證錯誤"},
                    "20":{"code": 20, "message": "用戶驗證資料成功"}
                    }
   
    def get_result(value):
        
        command = str(value)

        return CodeMessageEnum.CODE_MESSAGE.value.get(command)
    



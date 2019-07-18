# 返回的状态码

class RET:
    OK                  = "0"
    DBERR               = "1"
    NODATA              = "2"
    DATAEXIST           = "3"
    DATAERR             = "4"
    UNLOGINERR          = "5"
    LOGINERR            = "6"
    PARAMERR            = "7"
    THIRDERR            = "8"
    IOERR               = "9"


error_map = {
    RET.OK                    : u"成功",
    RET.DBERR                 : u"数据库查询错误",
    RET.NODATA                : u"无数据",
    RET.DATAEXIST             : u"数据已存在",
    RET.DATAERR               : u"数据错误",

    RET.LOGINERR              : u"用户登录失败",
    RET.PARAMERR              : u"参数错误",

    RET.THIRDERR              : u"第三方系统错误",
    RET.IOERR                 : u"文件读写错误",

}

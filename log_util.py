from datetime import datetime as dt
import os,shutil,sys
class LoggerUtil():
    @staticmethod
    def get_log_file():
        filename ="淘宝拍单记录%s.txt" % (dt.now().strftime('%Y-%m-%d'))
        if not os.path.exists(filename):
            if not os.path.exists("template.txt"):
                with open("template.txt", "w", encoding="utf-8") as w:
                    w.write("日志记录:\n")
            shutil.copy("template.txt",filename)
        return filename
    @staticmethod
    def write_file_log(info=None):
        if info is None:
            info = "[%s]-[%s]"% (sys.exc_info()[0], sys.exc_info()[1])
        date_str = dt.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(LoggerUtil.get_log_file(), "a+", encoding="utf-8") as f:
            f.write("[%s]:%s\n" % (date_str, info))
            print("[%s]:%s\n" % (date_str, info))
if __name__ == '__main__':
    LoggerUtil.write_file_log("测试数据!");
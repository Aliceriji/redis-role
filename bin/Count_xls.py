# coding=utf-8
import xlwt,xlrd,os
from static.pro import PATH

def read_xls(file):
    All = xlrd.open_workbook(file)
    dic = {}
    for name in All.sheet_names():
        lis = [All.sheet_by_name(name).row_values(i) for i in range(len(All.sheet_by_name(name).col_values(0)))]
        dic[name] = lis
    return dic

def write_xls(_pd,file=os.path.join(PATH,'text.xls')):
    wb = xlwt.Workbook()
    if type(_pd) == dict:
        for name in _pd:
            [wb.add_sheet(name).write(I,J,o) for I,li in enumerate(_pd[name]) for J,o in enumerate(li)]
    else:
        [wb.add_sheet('text').write(I, J, o) for I, li in enumerate(_pd) for J, o in enumerate(li)]
    wb.save(file)
    print('当前保存文件:',file)
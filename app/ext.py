import os
import re
import datetime
import xlrd
import pandas as pd

from flata import Flata
from flata.storages import JSONStorage

from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_principal import (Permission, Principal, RoleNeed)
from flask_uploads import UploadSet, DOCUMENTS, DATA, ARCHIVES

bcrypt = Bcrypt()
login_manager = LoginManager()
principal = Principal()
file_excel = UploadSet('fileexcel', DOCUMENTS)
file_zip = UploadSet('filezip', ARCHIVES)
file_tem = UploadSet('template', DATA)
file_ork = UploadSet('fileokr', ('tsv',))


def excel_to_dict(file):
    df = pd.read_excel(file, keep_default_na=False)
    result_dict = {}
    for i in df.index:
        row_dict = {}
        for sam in df.columns:
            row_dict[sam] = str(df.loc[i][sam])
        result_dict[i] = row_dict
    return result_dict


def df2dict(df):
    result_dict = {}
    for i in df.index:
        row_dict = {}
        for sam in df.columns:
            row_dict[sam] = str(df.loc[i][sam])
        result_dict[i] = row_dict
    return result_dict


def str2time(str):
    if str and str != ' ':
        if len(str) == 6:
            time = datetime.datetime.strptime(str, '%Y%m')
        else:
            time = datetime.datetime.strptime(str, '%Y%m%d')
    else:
        time = None
    return time


def time_set(item):
    if item != ' ':
        if '.' in item:
            date = datetime.datetime.strptime(item, "%Y.%m.%d %H:%M")
        else:
            date = datetime.datetime.strptime(item, "%Y%m%d %H:%M")
        time = date.strftime('%Y-%m-%d %H:%M:%S')
    else:
        time = None
    return time


def get_seq_info(file):
    df = pd.read_excel(file, header=1, keep_default_na=False)
    df1 = df[['文件名(Run)', '迈景编号', '申请单号', '检测内容',
              'Barcode编号', '上机时间', '结束时间', '备注']].copy()
    return df1.groupby(pd.Grouper(key='文件名(Run)'))


def excel2dict(file):
    df = pd.read_excel(file, header=1, keep_default_na=False)

    for i in df['Run name'].unique():
        if i:
            run_name = i
    df['Run name'] = run_name
    for i in df['上机时间'].unique():
        if i:
            start_T = i
    df['上机时间'] = start_T
    for i in df['下机时间'].unique():
        if i:
            end_T = i
    df['下机时间'] = end_T
    dict_f = df2dict(df)
    return dict_f


def get_excel_title(file):
    data = xlrd.open_workbook(file)
    table = data.sheets()[0]
    title = table.row_values(0)[0].strip('上机信息表')
    return title


def listIR2dict(list):
    if list:
        title = list.pop(0)
        dict_mu = []
        for j in list:
            dict_row = {}
            for i in range(len(title)):
                dict_row[title[i]] = j[i]
            dict_mu.append(dict_row)
    else:
        dict_mu = []
    return dict_mu


def readFromJson(path_db, table_name):
    tb = Flata(path_db, storage=JSONStorage).table(table_name).all()[0]
    return tb


def saveInJson(db_path, dic, mg):
    db = Flata(db_path, storage=JSONStorage)
    tb = db.table(mg)
    dic_mu = {}
    for name, mu_list in dic.items():
        dic_mu[name] = listIR2dict(mu_list)
    tb.insert(dic_mu)
    return tb


def json_update(path_db, mg, key, val, new_dict):
    db = Flata(path_db, storage=JSONStorage)
    table = db.table(mg)
    dic_re = table.all()[0]
    for row in dic_re['out_Report']:
        if row[key] == val:
            if new_dict:
                for k, v in new_dict.items():
                    row[k] = v
    table.purge()
    table.insert(dic_re)
    return table


def ir2report(ir_result):
    Protein, Function = ir_result.get("protein").split('|')[0], ir_result.get("function").split('|')[0]
    Re_GENE, De_GENE = [], []
    if 'del' in ir_result.get("coding").split('|')[0]:
        GENE = ir_result.get("coding").split('|')[0].split('del')[-1]
        Re_GENE, De_GENE = GENE, GENE + '/-'
    elif 'ins' in ir_result.get("coding").split('|')[0]:
        GENE = ir_result.get("coding").split('|')[0].split('ins')[-1]
        Re_GENE, De_GENE = '-', '-/' + GENE
    else:
        GENE = ir_result.get("coding").split('|')[0][-3:].split('>')
        Re_GENE, De_GENE = GENE[0], GENE[0] + "/" + GENE[-1]

    rep_P = {"Ala": "A", "Arg": "R", "Asn": "N", "Asp": "D", "Cys": "C", "Gln": "Q", "Glu": "E", "Gly": "G",
             "His": "H",
             "Ile": "I", "Leu": "L", "Lys": "K", "Met": "M", "Phe": "F", "Pro": "P", "Ser": "S", "Thr": "T",
             "Trp": "W",
             "Tyr": "Y", "Val": "V", "p.": "", }
    rep_F = {'missense': '错义突变', 'nonsense': '无义突变', 'nonframeshiftDeletion': '非移码缺失突变',
             'frameshiftDeletion': '移码缺失突变', 'nonframeshiftInsertion': '非移码插入突变', 'frameshiftInsertion': '移码插入突变',
             'nonframeshiftBlockSubstitution': '非移码插入突变'}

    rep_P, rep_F = dict((re.escape(k1), v1) for k1, v1 in rep_P.items()), dict(
        (re.escape(k2), v2) for k2, v2 in rep_F.items())

    pattern_P, pattern_F = re.compile("|".join(rep_P.keys())), re.compile("|".join(rep_F.keys()))

    Protein, Function = pattern_P.sub(lambda n: rep_P[re.escape(n.group(0))], Protein), pattern_F.sub(
        lambda n: rep_F[re.escape(n.group(0))], Function)

    Name = ir_result.get("gene").split('|')[0] + ' ' + Protein
    Name_a = ir_result.get('transcript').split('|')[0] + '(' + ir_result.get("gene").split('|')[
        0] + ')' \
             + ':' + ir_result.get("coding").split('|')[0] + ' (' + \
             ir_result.get('protein').split('|')[0] + ')'

    dic_report = {'基因': ir_result.get("gene").split('|')[0], '检测的突变类型': ir_result.get('type').split('|')[0],
                  '变异全称': Name_a,
                  '突变频率': ir_result.get('AF').split(',')[0], '临床突变常用名称': Name,
                  '支持序列数': ir_result.get('FAO'), 'maf': ir_result.get('maf'),
                  '外显子': ir_result.get('exon').split('|')[0],
                  '功能影响': Function, '参考基因型': Re_GENE, '检测基因型': De_GENE,
                  '位置': ir_result.get('# locus')}
    return dic_report


def saveTemplate(path_db, item, dic):
    db = Flata(path_db, storage=JSONStorage)
    if db.get(item):
        tb = db.table(item)
        tb.purge()
    else:
        tb = db.table(item)
    tb.insert(dic)


def readJson(path_db):
    db = Flata(path_db, storage=JSONStorage)
    dic = db.all()
    return dic


def okr_c(str_okr):
    pat = '(.+)(\(\d+\))'
    m = re.match(pat, str_okr)
    if m:
        return [m.group(1), m.group(2)]
    else:
        return [str_okr, '']

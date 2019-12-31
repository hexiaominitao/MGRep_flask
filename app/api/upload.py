import os
import json

from flask_restful import (reqparse, Resource, fields, request)
from flask import (jsonify, current_app, abort)
from werkzeug.datastructures import FileStorage
from sqlalchemy import and_

from app.models import db
from app.models.sample import SampleInfo, PathologyInfo
from app.models.patient import PatientInfo, TreatInfo, FamilyInfo
from app.models.run_info import RunInfo, SeqInfo
from app.ext import file_excel, file_zip, file_tem,file_ork, excel_to_dict, str2time, get_seq_info, df2dict, time_set, \
    excel2dict, get_excel_title, saveTemplate, readJson
from app.z_lib.ir import unzip_file, ir10087
from app.z_lib.okr_ext import fileokr_to_dict,save_okr


class SampleInfoUpload(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('file', type=FileStorage, required=True,
                                 help='file')
        super(SampleInfoUpload, self).__init__()

    def get(self):
        # list_name = []
        # for row in TreatInfo.__table__.columns.keys():
        #     # list_name.append(row)
        #     print("'{}':self.{},".format(row,row))
        # for row in FamilyInfo.__table__.columns.keys():
        #     # list_name.append(row)
        #     print("'{}':self.{},".format(row,row))
        # # print(list_name)

        # pat = PatientInfo.query.filter(PatientInfo.name == '钟万富').first()
        # sam = pat.sample_info
        # print(sam[0].seq_date)
        sam = SampleInfo.query.get(1)
        pat = sam.patient_info
        print(pat.id)
        return 'hello'

    def post(self):
        filename = file_excel.save(request.files['file'])
        file = file_excel.path(filename)
        try:
            dict_sam = excel_to_dict(file)
            for dict_val in dict_sam.values():
                print(dict_val)
                pat = PatientInfo.query.filter(PatientInfo.name == dict_val.get('患者姓名')).first()
                if pat:
                    pass
                else:
                    pat = PatientInfo(name=dict_val.get('患者姓名'), age=dict_val.get('病人年龄'),
                                      gender=dict_val.get('病人性别'), nation=dict_val.get('民族'),
                                      origo=dict_val.get('籍贯'), contact=dict_val.get('病人联系方式'),
                                      ID_number=dict_val.get('病人身份证号码'), other_diseases=dict_val.get('有无其他基因疾病'),
                                      smoke=dict_val.get('有无吸烟史'))

                    db.session.add(pat)
                    db.session.commit()
                if SampleInfo.query.filter(and_(SampleInfo.req_mg == dict_val.get('申请单号'),
                                                SampleInfo.mg_id == dict_val.get('迈景编号'))).first():
                    pass
                else:
                    sam = SampleInfo(mg_id=dict_val.get('迈景编号'), req_mg=dict_val.get('申请单号'),
                                     seq_item=dict_val.get('检测项目'), seq_type=dict_val.get('项目类型'),
                                     doctor=dict_val.get('医生姓名'), hosptial=dict_val.get('医院名称'),
                                     room=dict_val.get('科室'), diagnosis=dict_val.get('临床诊断'),
                                     diagnosis_date=str2time(dict_val.get('诊断日期')), pathological=dict_val.get('病理诊断'),
                                     pathological_date=str2time(dict_val.get('诊断日期.1')),
                                     recive_date=str2time(dict_val.get('病理样本收到日期')),
                                     mode_of_trans=dict_val.get('运输方式'),
                                     send_sample_date=str2time(dict_val.get('送检日期')),
                                     reciver=dict_val.get('收样人'), recive_room_date=str2time(dict_val.get('收样日期')),
                                     sample_status=dict_val.get('状态是否正常'), sample_type=dict_val.get('样本类型'),
                                     sample_size=dict_val.get('样本来源'), sample_count=dict_val.get('数量'),
                                     seq_date=str2time(dict_val.get('检测日期')), note=dict_val.get('备注'),
                                     recorder=dict_val.get('录入'), reviewer=dict_val.get('审核'))
                    tre_h = TreatInfo(name='化疗', is_treat=dict_val.get('是否接受化疗'),
                                      star_time=str2time(dict_val.get('开始时间')),
                                      end_time=str2time(dict_val.get('结束时间')), effect=dict_val.get('治疗效果'))
                    tre_f = TreatInfo(name='放疗', is_treat=dict_val.get('是否放疗'),
                                      star_time=str2time(dict_val.get('起始时间')),
                                      end_time=str2time(dict_val.get('结束时间.2')), effect=dict_val.get('治疗效果.2'))
                    tre_b = TreatInfo(name='靶向治疗', is_treat=dict_val.get('是否靶向药治疗'),
                                      star_time=str2time(dict_val.get('开始时间.1')),
                                      end_time=str2time(dict_val.get('结束时间.1')), effect=dict_val.get('治疗效果.1'))
                    fam = FamilyInfo(is_family=dict_val.get('有无家族遗传疾病'))
                    print(((dict_val.get('标本内细胞总量'))))
                    patho = PathologyInfo(pathology=dict_val.get('病理审核'), cell_count=dict_val.get('标本内细胞总量'),
                                          cell_content=float(dict_val.get('肿瘤细胞含量')), spical_note=dict_val.get('特殊说明'))
                    db.session.add(sam)
                    db.session.add(patho)
                    sam.pathology_info.append(patho)
                    db.session.add(tre_b)
                    db.session.add(tre_f)
                    db.session.add(tre_h)
                    db.session.add(fam)
                    pat.sample_info.append(sam)
                    pat.treat_info.append(tre_b)
                    pat.treat_info.append(tre_f)
                    pat.treat_info.append(tre_h)
                    pat.family_info.append(fam)
                db.session.commit()

            msg = '文件上传成功!'
        except IOError:
            msg = '文件有问题,请检查后再上传!!!!!'
        os.remove(file)
        return {'msg': msg}, 200


class RunInfoUpload(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('file', type=FileStorage, required=True,
                                 help='file')
        super(RunInfoUpload, self).__init__()

    def post(self):
        filename = file_excel.save(request.files['file'])
        file = file_excel.path(filename)
        try:
            title = get_excel_title(file)
            print(title)
            if title in ['S5', 'PGM', 's5', 'pgm']:
                df_seq = get_seq_info(file)
                for name, df in df_seq:
                    if name:
                        dict_run = df2dict(df)
                        for dict_val in dict_run.values():
                            run = RunInfo.query.filter(RunInfo.name == name).first()
                            if run:
                                pass
                            else:
                                run = RunInfo(name=name, platform=title,
                                              start_T=time_set(dict_val.get('上机时间')),
                                              end_T=time_set(dict_val.get('结束时间')))
                                db.session.add(run)
                                db.session.commit()
                            seq = SeqInfo.query.filter(SeqInfo.sample_name == dict_val.get('迈景编号')).first()
                            if seq:
                                pass
                            else:
                                seq = SeqInfo(sample_name=dict_val.get('迈景编号'), sample_mg=dict_val.get('申请单号'),
                                              item=dict_val.get('检测内容'), barcode=dict_val.get('Barcode编号'),
                                              note=dict_val.get('备注'))
                                db.session.add(seq)
                                run.seq_info.append(seq)
                            db.session.commit()
            else:
                dict_run = excel2dict(file)
                for dict_val in dict_run.values():
                    run = RunInfo.query.filter(RunInfo.name == dict_val.get('Run name')).first()
                    if run:
                        pass
                    else:
                        run = RunInfo(name=dict_val.get('Run name'), platform=title,
                                      start_T=time_set(dict_val.get('上机时间')),
                                      end_T=time_set(dict_val.get('下机时间')))
                        db.session.add(run)
                        db.session.commit()
                    seq = SeqInfo.query.filter(SeqInfo.sample_name == dict_val.get('样本编号')).first()
                    if seq:
                        pass
                    else:
                        seq = SeqInfo(sample_name=dict_val.get('样本编号'),
                                      item=dict_val.get('检测项目'), barcode=dict_val.get('index(P7+P5)'),
                                      note=dict_val.get('备注'))
                        db.session.add(seq)
                        run.seq_info.append(seq)
                    db.session.commit()
            msg = '文件上传成功!'
        except IOError:
            msg = '文件有问题,请检查后再上传!!!!!'
        os.remove(file)
        return {'msg': msg}, 200


class IonRepZipUpload(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('file', type=FileStorage, required=True,
                                 help='file')
        super(IonRepZipUpload, self).__init__()

    def post(self):
        filename = file_zip.save(request.files['file'])
        print(filename)
        return {'msg': 'hello'}


class TemplateUpload(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('file', type=FileStorage, required=True,
                                 help='file')
        super(TemplateUpload, self).__init__()

    def post(self):
        filename = file_tem.save(request.files['file'])
        file = file_tem.path(filename)
        try:
            my_dic = readJson(file)
            dic = my_dic['template'][0]
            print(dic)
            path_db = os.path.join(current_app.config['TEMPLATE_REPORT'],'template.json')
            saveTemplate(path_db,dic['项目'],dic)
        except IOError:
            msg = '文件有问题'
        os.remove(file)
        return {'msg': 'hello'}


class OKRUpload(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('file', type=FileStorage, required=True,
                                 help='file')
        # self.parser.add_argument('mg_id',type=str)
        super(OKRUpload, self).__init__()

    def post(self):
        mg_id = request.form.get('mg_id') # 获取文件参数
        filename = file_ork.save(request.files['file'])
        file = file_ork.path(filename)
        sample = SampleInfo.query.filter(SampleInfo.mg_id == mg_id).first()
        req_mg = sample.req_mg
        path_report = current_app.config['REPORT_FILE']
        path_db = os.path.join(path_report, req_mg, '{}_okr.json'.format(req_mg))
        dict_okr = fileokr_to_dict(file)
        save_okr(path_db,dict_okr)
        os.remove(file)
        return {'msg': 'hello'}
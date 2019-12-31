import json
import re

from flask import (jsonify)
from flask_login import current_user
from flask_restful import (reqparse, Resource, fields, request)

from app.models import db
from app.models.sample import SampleInfo, Tag
from app.models.patient import PatientInfo, TreatInfo, FamilyInfo
from app.models.run_info import RunInfo, SeqInfo


class GetAllSample(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('val', required=True, type=str,
                                 help='迈景编号/申请单号/患者姓名')

    def get(self):
        all_sample = {}
        list_sample = []
        sams = SampleInfo.query.all()
        for sam in sams:
            pat = sam.patient_info
            dic_sam = sam.to_dict()
            dic_sam['patient_name'] = pat.name
            list_sample.append(dic_sam)
        all_sample['all_sample'] = list_sample
        return jsonify(all_sample)


class GetSampleById(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('mg', type=str,
                                 help='迈景编号')

    def get(self):
        args = self.parser.parse_args()
        mg_id = args.get('mg')
        sam = SampleInfo.query.filter(SampleInfo.mg_id == mg_id).first()
        pat = sam.patient_info
        sample = {}
        dict_sam = sam.to_dict()
        dict_sam['patient_name'] = pat.name
        sample['sample'] = dict_sam
        return jsonify(sample)


class GetSampleByName(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str,
                                 help='姓名')

    def get(self):
        args = self.parser.parse_args()
        name = args.get('name')
        # print(name)
        pat = PatientInfo.query.filter(PatientInfo.name == name).first()
        sample = {}
        dict_sam = pat.to_dict()
        sample['sample'] = dict_sam
        return jsonify(sample)


class GetRunInfo(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('page', type=int, help='页码')
        self.parser.add_argument('page_per', type=int, help='每页数量')
        self.parser.add_argument('id', help='样本id')

    def get(self):
        run_info = {}
        args = self.parser.parse_args()
        page = args.get('page')
        page_per = args.get('page_per')
        all_run = RunInfo.query.all()
        run_info['total'] = len(all_run)
        runs = RunInfo.query.order_by(RunInfo.start_T.desc()). \
            paginate(page=page, per_page=page_per, error_out=False)
        list_run = []
        for run in runs.items:
            list_run.append(run.to_dict())
        run_info['run'] = list_run
        return jsonify(run_info)

    def post(self):
        args = self.parser.parse_args()
        id = args.get('id')
        run = RunInfo.query.filter(RunInfo.id == id).first()
        run_id = run.name
        db.session.delete(run)
        db.session.commit()
        return {'msg': '{}删除完成'.format(run_id)}


class GetSeqInfo(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, help='文件名')
        self.parser.add_argument('sams', help='报告', action='append')

    def get(self):
        args = self.parser.parse_args()
        run_info = {}
        run_name = args.get('name')
        run = RunInfo.query.filter(RunInfo.name == run_name).first()
        run_info['run'] = run.to_dict()
        list_seq = []
        for seq in run.seq_info:
            list_seq.append(seq.to_dict())
        run_info['seq'] = list_seq
        return jsonify(run_info)

    def post(self):
        data = request.get_data()
        sams = (json.loads(data)['sams'])
        err = ''
        report = ''
        mmsg = ''
        user = '伞兵一号'
        for sam in sams:
            sample = sam.get('sample_name')
            if sample.startswith('MG'):
                s = '(MG\d+)(\w{2})?(-\d)?'
                m = re.match(s, sample)
                if m:
                    # sam_name = m.group(1) + m.group(3) if m.group(3) else m.group(1)
                    sam_name = m.group(1)
                    sam_info = SampleInfo.query.filter(SampleInfo.mg_id == sam_name).first()
                    if sam_info:
                        is_rep = 0
                        tags = []
                        for tag in sam_info.tags:
                            tags.append(tag.name)
                        if tags:
                            for tagg in tags:
                                if '承包中' in tagg:
                                    uuser = tagg.strip('承包中....')
                                    is_rep = 1
                        if is_rep:
                            mmsg += '{}已经被{}承包\t'.format(sam_name, uuser)
                        else:
                            tag = Tag.query.filter(Tag.name == '{}承包中....'.format(user)).first()
                            if tag:
                                pass
                            else:
                                tag = Tag(name='{}承包中....'.format(user), description='报告正处于制作过程中')
                            db.session.add(tag)
                            sam_info.tags.append(tag)
                            db.session.commit()
                            mmsg += '成功承包{}这片鱼塘\t'.format(sam_name)
                    else:
                        mmsg += '请上传{}对应的样本信息\t'.format(sam_name)


            else:
                err += sample + '\t'


        return {'msg': mmsg, 'err': '{}'.format(err)}


class GetMGid(Resource):
    def get(self):
        seqs = SeqInfo.query.order_by(SeqInfo.id.desc()).all()
        all_mg_id = {}
        list_mg_id = []
        for seq in seqs:
            dict_mg_id = {}
            dict_mg_id['key'] = seq.id
            dict_mg_id['label'] = seq.sample_name
            list_mg_id.append(dict_mg_id)
        all_mg_id['data'] = list_mg_id
        return jsonify(all_mg_id)

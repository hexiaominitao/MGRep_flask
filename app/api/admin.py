import json, os

from flask import (jsonify, current_app)
from flask_restful import (reqparse, Resource, fields, request)

from app.models import db
from app.models.patient import PatientInfo
from app.models.sample import SampleInfo
from app.models.user import User
from app.models.template import TemplateConfig, TemplateGeneCard

from app.ext import readJson


class AdminUser(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, help='pass')

    def get(self):
        users = User.query.all()
        dict_user = {}
        list_user = []
        for user in users:
            dic_user = {}
            list_role = []
            dic_user['id'] = user.id
            dic_user['username'] = user.username
            for role in user.roles:
                list_role.append(role.name)
            dic_user['roles'] = list_role
            list_user.append(dic_user)
        dict_user['user'] = list_user
        return jsonify(dict_user)

    def post(self):
        pass


class AdminSample(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('page', type=int, help='页码')
        self.parser.add_argument('page_per', type=int, help='每页数量')
        self.parser.add_argument('id', type=int, help='样本id')

    def get(self):
        args = self.parser.parse_args()
        page = args.get('page')
        page_per = args.get('page_per')
        sams = SampleInfo.query.order_by(SampleInfo.id.desc()).paginate(page=page, per_page=page_per, error_out=False)
        dict_sam = {}
        list_sam = []
        for sam in sams.items:
            list_patho = []
            dic_sam = sam.to_dict()
            for pa in sam.pathology_info:
                list_patho.append(pa.to_dict())
            dic_sam['pathology_info'] = list_patho
            list_sam.append(dic_sam)
        dict_sam['sample'] = list_sam
        dict_sam['total'] = len(SampleInfo.query.all())
        return jsonify(dict_sam)

    def post(self):
        args = self.parser.parse_args()
        id = args.get('id')
        sam = SampleInfo.query.filter(SampleInfo.id == id).first()
        mg = sam.mg_id
        db.session.delete(sam)
        db.session.commit()
        return {'msg': '{}删除成功'.format(mg)}, 200


class AdminPatient(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('page', type=int, help='页码')
        self.parser.add_argument('page_per', type=int, help='每页数量')
        self.parser.add_argument('id', type=int, help='样本id')

    def get(self):
        args = self.parser.parse_args()
        page = args.get('page')
        page_per = args.get('page_per')
        print(page_per)
        pats = PatientInfo.query.order_by(PatientInfo.id.desc()).paginate(page=page, per_page=page_per, error_out=False)
        dict_pat = {}
        list_pat = []
        for pat in pats.items:
            list_sam = []
            dic_pat = pat.to_dict()
            for pa in pat.sample_info:
                list_sam.append(pa.to_dict())
            dic_pat['sample_info'] = list_sam
            list_pat.append(dic_pat)
        dict_pat['patient'] = list_pat
        dict_pat['total'] = len(PatientInfo.query.all())
        return jsonify(dict_pat)

    def post(self):
        args = self.parser.parse_args()
        id = args.get('id')
        sam = PatientInfo.query.filter(PatientInfo.id == id).first()
        mg = sam.name
        db.session.delete(sam)
        db.session.commit()
        return {'msg': '{}删除成功'.format(mg)}, 200


class AdminTemplate(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, help='报告类型')

    def get(self):
        args = self.parser.parse_args()
        name = args.get('name')
        dict_tem = {}
        list_tem = []
        if name:
            path_db = os.path.join(current_app.config['TEMPLATE_REPORT'], 'template.json')
            tem = readJson(path_db)[name]
            print(tem)
            list_tem.append(tem)
        else:
            path_db = os.path.join(current_app.config['TEMPLATE_REPORT'], 'template.json')
            tems = readJson(path_db)
            # print(tems)

            for tem in tems.values():
                list_tem.append(tem[0])
        dict_tem['all_template'] = list_tem
        return jsonify(dict_tem)

    def post(self):
        data = request.get_data()
        templates = (json.loads(data)['templates'])
        print(templates.get('seq_content'))

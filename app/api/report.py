import json
import re
import os

from flask_weasyprint import HTML

from flask import (jsonify, current_app, url_for, send_from_directory, render_template)
from flask_restful import (reqparse, Resource, fields, request)
from sqlalchemy import func, or_, and_

from app.models import db
from app.models.sample import SampleInfo, Tag
from app.models.patient import PatientInfo, TreatInfo, FamilyInfo
from app.models.report import Report, Mutation, MutationTag, Explanation

from app.ext import saveInJson, json_update, readFromJson, readJson
from app.z_lib.ir import unzip_file, ir10087


class ReportStart(Resource):
    '''
    报告开始制作:承包
    '''

    # todo 添加真实用户

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('page', type=int, help='页码')
        self.parser.add_argument('page_per', type=int, help='每页数量')
        self.parser.add_argument('sams', help='报告', action='append')

    def get(self):
        args = self.parser.parse_args()
        page = args.get('page')
        page_per = args.get('page_per')
        sams = SampleInfo.query.order_by(SampleInfo.id.desc()).paginate(page=page, per_page=page_per, error_out=False)
        dict_sam = {}  # 保存样本的字典
        list_sam = []
        for sam in sams.items:
            list_patho = []
            dic_sam = sam.to_dict()
            for pa in sam.pathology_info:
                list_patho.append(pa.to_dict())
            dic_sam['pathology_info'] = list_patho
            tags = []
            my_tag = ''
            for tag in sam.tags:
                if '承包中' in tag.name:
                    tags.append(tag.name)
                    my_tag = tag.name
            dic_sam['tag'] = my_tag
            for tagg in tags:
                if '承包中' in tagg:
                    list_sam.append(dic_sam)

        dict_sam['sample'] = list_sam
        dict_sam['total'] = len(SampleInfo.query.all())
        return jsonify(dict_sam)

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
                    is_rep = 0
                    tags = []
                    for tag in sam_info.tags:
                        tags.append(tag.name)
                    if tags:
                        for tagg in tags:
                            if '打磨中' in tagg:
                                uuser = tagg.strip('打磨中....')
                                is_rep = 1
                    if is_rep:
                        mmsg = '{}正在被{}打磨'.format(sam_name, uuser)
                    else:
                        tag = Tag.query.filter(Tag.name == '{}打磨中....'.format(user)).first()
                        if tag:
                            pass
                        else:
                            tag = Tag(name='{}打磨中....'.format(user), description='报告正处于打磨过程中')
                        db.session.add(tag)
                        sam_info.tags.append(tag)
                        db.session.commit()
                        mmsg += '即将开始艰难的打磨{}这份报告'.format(sam_name)


            else:
                err += sample + '\t'

        return {'msg': mmsg, 'err': '{}'.format(err)}


class ReportMutationList(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('mg', type=str, help='迈景编号')

    def get(self):
        args = self.parser.parse_args()
        mg_id = args.get('mg')
        sample = SampleInfo.query.filter(SampleInfo.mg_id == mg_id).first()
        req_mg = sample.req_mg
        path_report = current_app.config['REPORT_FILE']
        path_zip = current_app.config['UPLOADED_FILEZIP_DEST']
        path_unzip = current_app.config['UNZIP_FILE']
        tsv = unzip_file(path_report, path_zip, path_unzip, mg_id, req_mg)
        ir_result = ir10087(req_mg, tsv, path_report)
        path_report = current_app.config['REPORT_FILE']
        path_db = os.path.join(path_report, req_mg, '{}.json'.format(req_mg))
        if not os.path.exists(path_db):
            print('hello')
            saveInJson(path_db, ir_result, req_mg)

        tb = readFromJson(path_db, req_mg)
        report = tb['out_Report']

        return {'msg': '共检测到{}个突变'.format(len(report))}


class IRList(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('mg', type=str, help='迈景编号')

    def get(self):
        args = self.parser.parse_args()
        mg_id = args.get('mg')
        sample = SampleInfo.query.filter(SampleInfo.mg_id == mg_id).first()
        req_mg = sample.req_mg
        path_report = current_app.config['REPORT_FILE']
        path_db = os.path.join(path_report, req_mg, '{}.json'.format(req_mg))
        dic = readJson(path_db)
        # print(dic[req_mg][0].keys())
        dic_list = {}
        dic_list['all_ir_list'] = dic[req_mg][0]['out_ir']
        dic_list['msg'] = 'hello'
        dic_col = []

        for k in (dic[req_mg][0]['out_ir'][0]).keys():
            dic_te = {}
            dic_te['title'] = k
            dic_te['key'] = k
            dic_te['width'] = '120'
            dic_col.append(dic_te)
        return jsonify(dic_list)


'''
        for row in report:
            gene = row.get('基因')
            mu_type = row.get('检测的突变类型')
            mu_name = row.get('变异全称')
            mu_af = row.get('突变频率')
            mu_name_usual = row.get('临床突变常用名称')
            reads = row.get('支持序列数')
            maf = row.get('maf')
            exon = row.get('外显子')
            fu_type = row.get('功能影响')
            locus = row.get('位置')
            mutation = Mutation.query.filter(
                and_(Mutation.mg_id == mg_id, Mutation.mu_name_usual == mu_name_usual)).first()
            if mutation:
                # print(mutation.mg_id)
                pass
            else:
                mutation = Mutation(mg_id=mg_id, gene=gene, mu_type=mu_type, mu_name=mu_name, mu_af=mu_af,
                                    mu_name_usual=mu_name_usual, reads=reads, maf=maf, exon=exon,
                                    fu_type=fu_type, locus=locus)
                db.session.add(mutation)
                db.session.commit()


'''


# 获取突变信息,未添加report_id
class GetMutationList(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('mg', type=str, help='迈景编号')
        self.parser.add_argument('sams', help='报告', action='append')

    def get(self):
        args = self.parser.parse_args()
        mg_id = args.get('mg')
        sample = SampleInfo.query.filter(SampleInfo.mg_id == mg_id).first()
        req_mg = sample.req_mg
        path_report = current_app.config['REPORT_FILE']
        path_db = os.path.join(path_report, req_mg, '{}.json'.format(req_mg))
        dic = readJson(path_db)
        dict_mu = {}
        dict_mu['mutation'] = dic[req_mg][0]['out_Report']
        dict_mu['total'] = len(dict_mu['mutation'])
        # print(dict_mu['mutation'])
        return jsonify(dict_mu)

    def post(self):
        data = request.get_data()
        sams = (json.loads(data)['sams'])
        mg_id = (json.loads(data)['mg_id'])
        sample = SampleInfo.query.filter(SampleInfo.mg_id == mg_id).first()
        req_mg = sample.req_mg
        path_report = current_app.config['REPORT_FILE']
        path_db = os.path.join(path_report, req_mg, '{}.json'.format(req_mg))
        user = '伞兵一号'
        mmsg = 'hello'
        # json_update()
        for row in sams:
            # print(row)
            gene = row.get('基因')
            mu_type = row.get('检测的突变类型')
            mu_name = row.get('变异全称')
            mu_af = row.get('突变频率')
            mu_name_usual = row.get('临床突变常用名称')
            reads = row.get('支持序列数')
            maf = row.get('maf')
            exon = row.get('外显子')
            fu_type = row.get('功能影响')
            locus = row.get('位置')
            mutation = Mutation.query.filter(
                and_(Mutation.mg_id == mg_id, Mutation.mu_name_usual == mu_name_usual)).first()
            if mutation:
                # print(mutation.mg_id)
                pass
            else:
                mutation = Mutation(mg_id=mg_id, gene=gene, mu_type=mu_type, mu_name=mu_name, mu_af=mu_af,
                                    mu_name_usual=mu_name_usual, reads=reads, maf=maf, exon=exon,
                                    fu_type=fu_type, locus=locus)
                db.session.add(mutation)
                tag = MutationTag.query.filter(MutationTag.name == '{}审核通过'.format(user)).first()

                if tag:
                    pass
                else:
                    tag = MutationTag(name='{}审核通过'.format(user))
                    mmsg = '审核通过'
                #     print(user)
                # print(tag.name)
                print(tag.name)
                db.session.add(tag)
                mutation.tags.append(tag)
                db.session.commit()
                json_update(path_db, req_mg, '变异全称', row.get('变异全称'), {'tag': tag.name})

            # id = sam.get('id')
            # mu = Mutation.query.filter(Mutation.id == id).first()
            # checked = 0
            # tags = []
            # for tag in mu.tag:
            #     tags.append(tag.name)
            # if tags:
            #     for tagg in tags:
            #         if '通过' in tagg:
            #             uuser = tagg.strip('审核通过')
            #             checked = 1
            # if checked:
            #     mmsg = '通过'
            # else:
            #     tag = MutationTag.query.filter(Tag.name == '{}审核通过'.format(user)).first()
            #     if tag:
            #         pass
            #     else:
            #         tag = MutationTag(name='{}审核通过'.format(user))
            #         mmsg = '审核通过'
            #         print(user)
            #     print(tag.name)
            #     db.session.add(tag)
            #     mu.tag.append(tag)
            #     db.session.commit()

        return {'msg': mmsg}

    def delete(self):
        data = request.get_data()
        sams = (json.loads(data)['sams'])
        mg_id = (json.loads(data)['mg_id'])
        user = '伞兵一号'
        sample = SampleInfo.query.filter(SampleInfo.mg_id == mg_id).first()
        req_mg = sample.req_mg
        path_report = current_app.config['REPORT_FILE']
        path_db = os.path.join(path_report, req_mg, '{}.json'.format(req_mg))
        for row in sams:
            print(row)
            mu_name_usual = row.get('临床突变常用名称')
            mutation = Mutation.query.filter(
                and_(Mutation.mg_id == mg_id, Mutation.mu_name_usual == mu_name_usual)).first()
            tag = MutationTag.query.filter(MutationTag.name == '{}审核通过'.format(user)).first()
            print(tag.name)
            print(mutation.tags[0].name)
            mutation.tags.remove(tag)
            db.session.delete(mutation)
            db.session.commit()
            json_update(path_db, req_mg, '变异全称', row.get('变异全称'), {'tag': ''})
        return {'msg': '已经从报告中移除所选突变'}


class CheckMutation(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('mg', type=str, help='迈景编号')

    def get(self):
        args = self.parser.parse_args()
        mg_id = args.get('mg')
        dic_mu = {}
        mutation = []
        mutations = Mutation.query.filter(Mutation.mg_id == mg_id).all()
        for mu in mutations:
            mutation.append(mu.to_dict())
        dic_mu['mutation'] = mutation
        return jsonify(dic_mu)

    def post(self):
        data = request.get_data()
        sams = (json.loads(data)['sams'])
        mg_id = (json.loads(data)['mg_id'])
        user = '伞兵一号'
        print(sams)
        id = sams['id']
        # mu = Mutation.query.filter(Mutation.id == id).first()
        # if mu:
        #     print('hello')
        print(sams)
        Mutation.query.filter(Mutation.id == id).update(sams)
        db.session.commit()
        return {'msg': '修改完成'}


dic_explanation = {
    'EGFR L858R': 'EGFR L858R错义突变是非小细胞肺癌常见的突变，该突变对肿瘤靶向药物EGFR TKIs(厄洛替尼，吉非替尼，埃克替尼，阿法替尼，奥希替尼和达克替尼)敏感，奥希替尼为一线首选靶向药物《非小细胞肺癌NCCN指南V7.2019》，其中获得CFDA批准且适用的EGFR TKIs有：厄洛替尼，吉非替尼，埃克替尼，阿法替尼和奥希替尼。'}


class ReportMutation(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('mg', type=str, help='迈景编号')
        self.parser.add_argument('sams', help='报告', action='append')

    def get(self):
        args = self.parser.parse_args()
        mg_id = args.get('mg')
        mutation = []
        mutations = Mutation.query.filter(Mutation.mg_id == mg_id).all()
        for mu in mutations:
            exp = mu.explanations
            if exp:
                pass
            else:
                explan = dic_explanation.get(mu.mu_name_usual)
                if explan:
                    pass
                else:
                    explan = '解释数据库未收录该变异!!!'
                Mutation.query.filter(Mutation.id == mu.id).update({'explanations': explan})
                db.session.commit()
        mutations = Mutation.query.filter(Mutation.mg_id == mg_id).all()
        for mu in mutations:
            mutation.append(mu.to_dict())
        dict_mu = {}
        dict_mu['mutation'] = mutation
        dict_mu['total'] = len(mutation)
        return jsonify(dict_mu)

    def post(self):
        data = request.get_data()
        sams = (json.loads(data)['sams'])

        for sam in sams:
            id = sam['id']
            Mutation.query.filter(Mutation.id == id).update(sam)
            db.session.commit()
        #     db.session.commit()
        return {'msg': '保存成功'}


class OkrEdit(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('mg', type=str, help='迈景编号')

    def get(self):
        args = self.parser.parse_args()
        mg_id = args.get('mg')
        sample = SampleInfo.query.filter(SampleInfo.mg_id == mg_id).first()
        req_mg = sample.req_mg
        path_report = current_app.config['REPORT_FILE']
        path_db = os.path.join(path_report, req_mg, '{}_okr.json'.format(req_mg))
        tb = readFromJson(path_db, 'okr')
        # print(type(tb))
        okr_data = {}
        okr_data['okr'] = (tb.get('临床上显著生物标志物')['临床上显著生物标志物'])
        return jsonify(okr_data)


class CreateReport(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('mg', type=str, help='迈景编号')

    def get(self):
        args = self.parser.parse_args()
        mg_id = args.get('mg')
        sam = SampleInfo.query.filter(SampleInfo.mg_id == mg_id).first()
        req_mg = sam.req_mg
        path_rep = os.path.join(current_app.config['REPORT_FILE'], req_mg)
        file_report = os.path.join(path_rep, '迈景基因检测报告_{}.pdf'.format(req_mg))

        mutations = Mutation.query.filter(Mutation.mg_id == mg_id).all()
        mutation = []
        for mu in mutations:
            for tag in mu.tags:
                if '审核通过' in tag.name:
                    mutation.append(mu)
        explanation = Explanation.query.filter(Explanation.mg_id == mg_id).all()
        html = render_template('report/12.html', sam=sam, mutation=mutation, explanation=explanation)
        HTML(string=html).write_pdf(file_report)

        return {'msg': '成功生成报告!'}

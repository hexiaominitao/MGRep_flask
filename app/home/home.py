import os
from os import path

from app.models import db
from app.models.sample import SampleInfo, Tag
from app.models.patient import PatientInfo, TreatInfo, FamilyInfo
from app.models.report import Report, Mutation, MutationTag, Explanation
from app.ext import readFromJson, okr_c

from flask_weasyprint import HTML, render_pdf
from flask import (render_template, Blueprint, redirect, send_from_directory, current_app)

home = Blueprint('home', __name__)


@home.route('/')
def index():
    return render_template('index.html')


@home.route('/igv/')
def igv():
    return render_template('igv/igv.html')


@home.route('/report/')
def report():
    return render_template('report/report.html')


@home.route('/report/575/')
def report_575():
    return render_template('report/575.html')


@home.route('/report/cover_12/')
def report_cover_12():
    return render_template('report/report_cover_12.html')


@home.route('/report/12/<mg_id>')
def report_12(mg_id):
    sam = SampleInfo.query.filter(SampleInfo.mg_id == mg_id).first()
    mutations = Mutation.query.filter(Mutation.mg_id == mg_id).all()

    req_mg = sam.req_mg
    path_rep = path.join(os.getcwd(), current_app.config['REPORT_FILE'], req_mg)
    file_report = os.path.join(path_rep, '迈景基因检测报告_{}.pdf'.format(req_mg))
    mutation = []
    for mu in mutations:
        for tag in mu.tag:
            if '审核通过' in tag.name:
                mutation.append(mu)
    explanation = Explanation.query.filter(Explanation.mg_id == mg_id).all()
    html = render_template('report/base_pgm.html', sam=sam, mutation=mutation, explanation=explanation)
    # return html
    # pdf = render_pdf(HTML(string=html))
    # HTML(string=html).write_pdf(file_report)
    #
    return render_pdf(HTML(string=html), download_filename='{}.pdf'.format(req_mg), automatic_download=True)


@home.route('/api/download/<mg_id>_<item>')
def download_pdf(mg_id, item):
    sam = SampleInfo.query.filter(SampleInfo.mg_id == mg_id).first()
    mutations = Mutation.query.filter(Mutation.mg_id == mg_id).all()

    req_mg = sam.req_mg
    tem_db_dir = current_app.config['TEMPLATE_REPORT']  # 模板配置文件路径
    path_rep = path.join(current_app.config['REPORT_FILE'], req_mg)  # 报告保存路径
    file_report = os.path.join(path_rep, '迈景基因检测报告_{}.pdf'.format(req_mg))
    if os.path.exists(file_report):
        os.remove(file_report)
    path_db = os.path.join(path_rep, '{}_okr.json'.format(req_mg))  # okr保存路径
    tb = readFromJson(path_db, 'okr')
    okr = tb.get('临床上显著生物标志物')['临床上显著生物标志物']

    list_okr = []
    for row in okr:
        dic_okr = {}
        for k, v in row.items():
            dic_okr[k] = okr_c(v)
        list_okr.append(dic_okr)

    cancer_okr = tb.get('样本癌症类型')
    target = tb.get('基因变异相应靶向治疗方案')['基因变异相应靶向治疗方案']
    mu_target = set()
    for row in target:
        mu_target.add(row['基因组改变'])
    mu_target = list(mu_target)
    mu_target.sort()
    dic_target = {}
    for mu in mu_target:
        list_mu = []
        for row in target:
            if row['基因组改变'] == mu:
                list_mu.append(row)
        dic_target[mu] = list_mu
    therapy_fda = list(tb.get('相关疗法详情').keys())

    def creat_dic_therapy(mu_target, fda):
        fda_the = {}
        for mu in mu_target:
            list_mu = []
            for row in fda:
                if row['基因组改变'] == mu:
                    list_mu.append(row)
            fda_the[mu] = list_mu
        return fda_the

    dic_thee = {}
    for thee in (list(therapy_fda)):
        dic_thee[thee] = creat_dic_therapy(mu_target, tb.get('相关疗法详情').get(thee).get('therapy'))
    dic_time = {}
    for thee in (list(therapy_fda)):
        dic_time[thee] = tb.get('相关疗法详情').get(thee).get('time')

    mutation = []
    for mu in mutations:
        for tag in mu.tags:
            if '审核通过' in tag.name:
                mutation.append(mu)

    html_cover = render_template('report/report_cover_12.html', item=item)
    path_db_tem = os.path.join(tem_db_dir, 'template.json')
    report_config = readFromJson(path_db_tem, item)

    gene_seq = (report_config['基因列表'])

    path_db_gene_list = os.path.join(tem_db_dir, 'gene_list.json')
    tb_gene_list = readFromJson(path_db_gene_list, 'gene_list')

    gene_list = []
    for g_row in gene_seq:
        gene = g_row['基因']
        for row in tb_gene_list.get('gene_list'):
            if row['基因'] == gene:
                gene_list.append(row)

    gene_list_one = gene_list.pop(0)

    # 转录本
    transcript_db = os.path.join(tem_db_dir, 'transcript.json')
    trans_gene = readFromJson(transcript_db, 'transcript')

    mu_re = Mutation.query.filter(Mutation.mg_id == mg_id).all()
    l_mutation = []
    name_mu = []
    for mu in mu_re:
        l_mutation.append(mu.to_dict())
        name_mu.append(mu.mu_name_usual + mu.fu_type)

    if len(name_mu) > 1:
        mu_name = ','.join(name_mu)
    else:
        mu_name = name_mu[0]

    dict_mutation = {'mu_count': len(l_mutation), 'mu_name': mu_name}

    # 处理突变
    out_result = []
    for g_row in gene_seq:
        gene = g_row['基因']
        mutation = g_row['检测的变异类型']
        ir_result = []
        for mu in l_mutation:
            if mu['gene'] == gene:
                ir_result.append(mu)
        if ir_result:
            pass
        else:
            ir_result = [{'mu_af': ' ', 'mu_name': '未检出', 'mu_name_usual': ' ', 'grade': ' '}]
        count = len(ir_result)
        result_rep = {'name': gene, 'mutation': mutation,
                      'result': ir_result, 'count': count}
        out_result.append(result_rep)

    gene_one = out_result.pop(0)

    def splitN(listS, n):
        for i in range(0, len(listS), n):
            yield listS[i:i + n]

    script_gene = [gene for gene in splitN([ge['基因'] for ge in gene_seq], 3)]
    script_rna = [gene for gene in splitN([ge['基因'] for ge in gene_seq if '融合' in ge['检测的变异类型']], 3)]

    html = render_template('report/base_pgm.html', sam=sam, dict_mutation=dict_mutation, l_mutation=l_mutation,
                           gene_list=gene_list, gene_list_one=gene_list_one, item=item, dic_thee=dic_thee,
                           dic_time=dic_time, report_config=report_config,
                           gene_one=gene_one, script_rna=script_rna,
                           trans_gene=trans_gene, script_gene=script_gene, out_result=out_result, list_okr=list_okr,
                           cancer_okr=cancer_okr, mu_target=mu_target, dic_target=dic_target)

    print(file_report)
    return render_pdf(HTML(string=html))
    # return html
    # HTML(string=html).write_pdf(file_report)
    # return send_from_directory(path_rep, '迈景基因检测报告_{}.pdf'.format(req_mg), as_attachment=True)

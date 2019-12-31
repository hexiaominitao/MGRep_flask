from flask_restful import Api
from . import api

my_api = Api(api)

# 用户相关
from app.api.user import LoginView, LoginOut, GetInfo

my_api.add_resource(LoginView, '/user/login')
my_api.add_resource(LoginOut, '/user/logout')
my_api.add_resource(GetInfo, '/user/get_info')

# 文件上传
from app.api.upload import SampleInfoUpload, RunInfoUpload, IonRepZipUpload, TemplateUpload, OKRUpload

my_api.add_resource(SampleInfoUpload, '/upload/sample_info_upload')  # 样本信息
my_api.add_resource(RunInfoUpload, '/upload/run_info_upload')  # 上机信息上传
my_api.add_resource(IonRepZipUpload, '/upload/ir_zip_upload')  # zip上传
my_api.add_resource(TemplateUpload, '/upload/template_json')  # 模板配置文件上传
my_api.add_resource(OKRUpload, '/upload/okr_upload')  # okr数据上传

# 数据获取
from app.api.get_data import GetAllSample, GetSampleById, GetSampleByName, GetRunInfo, GetSeqInfo, GetMGid

my_api.add_resource(GetAllSample, '/data/get_sample_info')  # 样本信息获取
my_api.add_resource(GetSampleById, '/data/get_sample_info/')
my_api.add_resource(GetSampleByName, '/data/get_sample_name/')
my_api.add_resource(GetRunInfo, '/data/get_run_info/')
my_api.add_resource(GetSeqInfo, '/data/get_seq_info/')
my_api.add_resource(GetMGid, '/data/get_mg_id/')

# admin
from app.api.admin import AdminUser, AdminSample, AdminPatient, AdminTemplate

my_api.add_resource(AdminUser, '/admin/user/')
my_api.add_resource(AdminSample, '/admin/sample/')
my_api.add_resource(AdminPatient, '/admin/patient/')
my_api.add_resource(AdminTemplate, '/admin/template/')

# qc
from app.api.qc import Select2QC

my_api.add_resource(Select2QC, '/qc/select/')

# report
from app.api.report import ReportStart, ReportMutationList, GetMutationList, ReportMutation, \
    CreateReport, IRList, CheckMutation, OkrEdit

my_api.add_resource(ReportStart, '/report/start/')
my_api.add_resource(ReportMutationList, '/report/mutation/')
my_api.add_resource(GetMutationList, '/report/mutation_list/')
my_api.add_resource(ReportMutation, '/report/mutation_check/')
my_api.add_resource(CreateReport, '/report/download/')
my_api.add_resource(IRList, '/report/irlist/')
my_api.add_resource(CheckMutation, '/report/check_mutation/')
my_api.add_resource(OkrEdit, '/report/get_okr/')

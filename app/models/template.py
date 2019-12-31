from app.models import db


class TemplateConfig(db.Model):
    __tablename__ = 'template_config'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50))  # 检测项目
    seq_content = db.Column(db.String(2000))  # 检测内容
    gene_detial = db.Column(db.String(2000))  # 结果详情
    method = db.Column(db.String(2000))  # 检测方法和局限性
    limit = db.Column(db.String(2000))  # 检测方法和局限性
    gene_list = db.Column(db.String(5000))  # 基因列表

    def to_dict(self):
        dict = {
            'id' : self.id,
            'name' : self.name,
            'seq_content' : self.seq_content,
            'gene_detail' : self.gene_detial,
            'method' : self.method,
            'limit' : self.limit,
            'gene_list' : self.gene_list
         }
        return dict


class TemplateGeneCard(db.Model):
    __tablename__ = 'template_gene_card'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(200))  # gene名称
    transcript = db.Column(db.String(200))  # 转录本
    gene_func = db.Column(db.String(2000))  # 基因功能
    gene_cancer = db.Column(db.String(2000))  # 基因与肿瘤的关系
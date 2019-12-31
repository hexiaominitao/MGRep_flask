from . import db


mu_tags = db.Table('mutation_tags',
                db.Column('mutation_id', db.Integer, db.ForeignKey('mutation.id')),
                db.Column('mutation_tag_id', db.Integer, db.ForeignKey('mutation_tag.id')))

# mu_explanation = db.Table('mutation_exp',
#                 db.Column('mutation_id', db.Integer, db.ForeignKey('mutation.id')),
#                 db.Column('explanation_id', db.Integer, db.ForeignKey('explanation.id')))


class Report(db.Model):
    __tablename__ = 'report'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    sample_info_id = db.Column(db.Integer(), db.ForeignKey('sample_info.id'))
    mutation = db.relationship('Mutation', backref='report', lazy='dynamic')
    # mutation = db.relationship('Mutation', backref='report', lazy='dynamic') # 注释信息
    # mutation = db.relationship('Mutation', backref='report', lazy='dynamic') # 药物信息


class Mutation(db.Model):
    __tablename__ = 'mutation'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    mg_id = db.Column(db.String(50), nullable=False) # 迈景编号
    gene = db.Column(db.String(200), nullable=False) # 基因名称
    mu_type = db.Column(db.String(50), nullable=False) # 检测的突变类型
    mu_name = db.Column(db.String(200), nullable=False) # 变异全称
    mu_af = db.Column(db.String(50), nullable=False) # 突变频率
    mu_name_usual = db.Column(db.String(200), nullable=False) # 临床突变常用名称
    reads = db.Column(db.String(50), nullable=False) # 支持序列数
    maf = db.Column(db.String(50), nullable=True) # maf
    exon = db.Column(db.String(50), nullable=True) # 外显子
    fu_type = db.Column(db.String(50), nullable=False) # 功能影响
    locus = db.Column(db.String(200), nullable=False)
    grade = db.Column(db.String(200), nullable=True) # 临床意义级别
    report_id = db.Column(db.Integer(), db.ForeignKey('report.id'))
    explanations = db.Column(db.String(2000), nullable=True)
    # tag = db.relationship('MutationTag', backref='mutation', lazy='dynamic')
    tags = db.relationship('MutationTag', secondary=mu_tags, back_populates='mutations')
    # explanations = db.relationship('Explanation', secondary=mu_explanation, back_populates='mutations')

    def to_dict(self):
        return {
            'id': self.id,
            'mg_id': self.mg_id,
            'gene': self.gene,
            'mu_type': self.mu_type,
            'mu_name': self.mu_name,
            'mu_af': self.mu_af,
            'mu_name_usual': self.mu_name_usual,
            'reads': self.reads,
            'maf': self.maf,
            'exon': self.exon,
            'fu_type': self.fu_type,
            'locus': self.locus,
            'grade': self.grade,
            'explanations': self.explanations
        }


class MutationTag(db.Model):
    __tablename__ = 'mutation_tag'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    mutations = db.relationship('Mutation',secondary=mu_tags, back_populates='tags')
    # mutation_id = db.Column(db.Integer(), db.ForeignKey('mutation.id'))


class Explanation(db.Model):
    __tablename__ = 'explanation'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    content = db.Column(db.String(2000), nullable=False)
    # mutations = db.relationship('Mutation', secondary=mu_explanation, back_populates='explanations')

# class ReportOkr(db.Model):
#     __tablename__ = 'report_okr'
#     id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
#     mg_id = db.Column(db.String(50), nullable=False)
#     mutation_name = db.Column(db.String(500), nullable=False)
#     cfda = db.Column(db.String(200), nullable=False)
#     fda = db.Column(db.String(200), nullable=False)

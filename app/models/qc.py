from . import db


class SampleQC(db.Model):
    __tablename__ = 'sample_qc'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    mg_id = db.Column(db.String(500), nullable=True)
    sample_info_id = db.Column(db.Integer(), db.ForeignKey('sample_info.id'))
    qc_file = db.relationship('QCFile', backref='sample_qc', lazy='dynamic')
    distill_qc = db.relationship('DistillQC', backref='sample_qc', lazy='dynamic')
    build_qc = db.relationship('BuildQC', backref='sample_qc', lazy='dynamic')
    run_qc = db.relationship('RunQC', backref='sample_qc', lazy='dynamic')
    seq_qc = db.relationship('SeqQC', backref='sample_qc', lazy='dynamic')
    analysis_qc = db.relationship('AnalysisQC', backref='sample_qc', lazy='dynamic')
    table_qc_id = db.Column(db.Integer(), db.ForeignKey('table_qc.id'))


class QCFile(db.Model):
    __tablename__ = 'qc_file'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    item = db.Column(db.String(50), nullable=True)  # 提取/建库/上机 ?
    file_path = db.Column(db.String(500), nullable=True)  # 质控文件路径
    sample_qc_id = db.Column(db.Integer(), db.ForeignKey('sample_qc.id'))


class DistillQC(db.Model):  # 提取质控
    __tablename__ = 'distill_qc'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    # sample_type = db.Column(db.String(50), nullable=True)
    # sample_count = db.Column(db.String(50), nullable=True)
    # blood_count = db.Column(db.String(50), nullable=True)
    # qubit = db.Column(db.String(50), nullable=True)
    # NGS_volume = db.Column(db.String(50), nullable=True)
    # QPCR_volume = db.Column(db.String(50), nullable=True)
    # volume = db.Column(db.String(50), nullable=True)
    # total = db.Column(db.String(50), nullable=True)
    # degrade = db.Column(db.String(50), nullable=True)
    sample_qc_id = db.Column(db.Integer(), db.ForeignKey('sample_qc.id'))


class BuildQC(db.Model):  # 建库质控
    __tablename__ = 'build_qc'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)

    sample_qc_id = db.Column(db.Integer(), db.ForeignKey('sample_qc.id'))


class RunQC(db.Model):  # 上机质控
    __tablename__ = 'run_qc'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)

    sample_qc_id = db.Column(db.Integer(), db.ForeignKey('sample_qc.id'))


class SeqQC(db.Model):  # 测序质控
    __tablename__ = 'seq_qc'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)

    sample_qc_id = db.Column(db.Integer(), db.ForeignKey('sample_qc.id'))


class AnalysisQC(db.Model):  # 生信分析质控
    __tablename__ = 'analysis_qc'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)

    sample_qc_id = db.Column(db.Integer(), db.ForeignKey('sample_qc.id'))


class TableQC(db.Model):
    __tablename__ = 'table_qc'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(500), nullable=True)
    sample_qc = db.relationship('SampleQC', backref='table_qc', lazy='dynamic')
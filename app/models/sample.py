from . import db

tags = db.Table('sample_tag',
                db.Column('sample_info_id', db.Integer, db.ForeignKey('sample_info.id')),
                db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')))


# 样本信息
class SampleInfo(db.Model):
    __tablename__ = 'sample_info'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    mg_id = db.Column(db.String(50), nullable=False)
    req_mg = db.Column(db.String(50), nullable=False)
    seq_item = db.Column(db.String(500), nullable=True)
    seq_type = db.Column(db.String(50), nullable=True)
    doctor = db.Column(db.String(50), nullable=True)
    hosptial = db.Column(db.String(50), nullable=True)
    room = db.Column(db.String(50), nullable=True)
    diagnosis = db.Column(db.String(500), nullable=True)
    diagnosis_date = db.Column(db.Date(), nullable=True)
    pathological = db.Column(db.String(500), nullable=True)
    pathological_date = db.Column(db.Date(), nullable=True)
    recive_date = db.Column(db.Date(), nullable=True)
    mode_of_trans = db.Column(db.String(50), nullable=True)
    send_sample_date = db.Column(db.Date(), nullable=True)
    reciver = db.Column(db.String(50), nullable=True)
    recive_room_date = db.Column(db.Date(), nullable=True)
    sample_status = db.Column(db.String(50), nullable=True)
    sample_type = db.Column(db.String(50), nullable=True)
    sample_size = db.Column(db.String(50), nullable=True)
    sample_count = db.Column(db.String(50), nullable=True)
    seq_date = db.Column(db.Date(), nullable=True)
    note = db.Column(db.String(500), nullable=True)
    recorder = db.Column(db.String(50), nullable=True)
    reviewer = db.Column(db.String(50), nullable=True)
    sample_qc = db.relationship('SampleQC', backref='sample_info', lazy='dynamic')
    report = db.relationship('Report', backref='sample_info', lazy='dynamic')
    pathology_info = db.relationship('PathologyInfo', backref='sample_info', lazy='dynamic')
    patient_id = db.Column(db.Integer(), db.ForeignKey('patient_info.id'))  # 病人信息
    # table_qc_id = db.Column(db.Integer(), db.ForeignKey('table_qc.id'))
    tags = db.relationship('Tag', secondary=tags, backref=db.backref('sample_info', lazy='dynamic'))

    # seq_info = db.relationship('SeqInfo', backref='sample_info', lazy='dynamic')

    def to_dict(self):
        dict = {
            "id": self.id,
            "mg_id": self.mg_id,
            "req_mg": self.req_mg,
            "seq_item": self.seq_item,
            "seq_type": self.seq_type,
            "doctor": self.doctor,
            "hosptial": self.hosptial,
            "room": self.room,
            "diagnosis": self.diagnosis,
            "diagnosis_date": self.diagnosis_date,
            "pathological": self.pathological,
            "pathological_date": self.pathological_date,
            "recive_date": self.recive_date,
            "mode_of_trans": self.mode_of_trans,
            "send_sample_date": self.send_sample_date,
            "reciver": self.reciver,
            "recive_room_date": self.recive_room_date,
            "sample_status": self.sample_status,
            "sample_type": self.sample_type,
            "sample_size": self.sample_size,
            "sample_count": self.sample_count,
            "seq_date": self.seq_date,
            "note": self.note,
            "recorder": self.recorder,
            "reviewer": self.reviewer
        }
        return dict


#  病理信息
class PathologyInfo(db.Model):
    __tablename__ = 'pathology_info'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    pathology = db.Column(db.String(500), nullable=True)
    view = db.Column(db.String(500), nullable=True)
    cell_count = db.Column(db.String(50), nullable=True)
    cell_content = db.Column(db.Float(), nullable=True)
    spical_note = db.Column(db.String(500), nullable=True)
    sample_info_id = db.Column(db.Integer(), db.ForeignKey('sample_info.id'))
    pathology_pic = db.relationship('PathologyPic', backref='pathology_info', lazy='dynamic')

    def to_dict(self):
        dict = {
            "id": self.id,
            'pathology': self.pathology,
            'view': self.view,
            'cell_count': self.cell_count,
            'cell_content': self.cell_content,
            'spical_note': self.spical_note
        }
        return dict


#  病理图片
class PathologyPic(db.Model):
    __tablename__ = 'pathology_pic'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    path = db.Column(db.String(500), nullable=True)
    pathology_info_id = db.Column(db.Integer(), db.ForeignKey('pathology_info.id'))


class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

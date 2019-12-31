from . import db


# 病人信息
class PatientInfo(db.Model):
    __tablename__ = 'patient_info'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=True)
    age = db.Column(db.String(50), nullable=True)
    gender = db.Column(db.String(50), nullable=True)
    nation = db.Column(db.String(50), nullable=True)
    origo = db.Column(db.String(50), nullable=True)
    contact = db.Column(db.String(50), nullable=True)
    ID_number = db.Column(db.String(50), nullable=True)
    other_diseases = db.Column(db.String(500), nullable=True)
    smoke = db.Column(db.String(50), nullable=True)
    sample_info = db.relationship('SampleInfo', backref='patient_info', lazy='dynamic')
    treat_info = db.relationship('TreatInfo', backref='patient_info', lazy='dynamic')
    family_info = db.relationship('FamilyInfo', backref='patient_info', lazy='dynamic')

    def to_dict(self):
        dict = {'id': self.id,
                'name': self.name,
                'age': self.age,
                'gender': self.gender,
                'nation': self.nation,
                'origo': self.origo,
                'contact': self.contact,
                'ID_number': self.ID_number,
                'other_diseases': self.other_diseases,
                'smoke': self.smoke}
        return dict


# 治疗信息
class TreatInfo(db.Model):
    __tablename__ = 'treat_info'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    is_treat = db.Column(db.String(50), nullable=True)
    name = db.Column(db.String(50), nullable=True)
    star_time = db.Column(db.Date(), nullable=True)
    end_time = db.Column(db.Date(), nullable=True)
    effect = db.Column(db.String(100), nullable=True)
    patient_id = db.Column(db.Integer(), db.ForeignKey('patient_info.id'))

    def to_dict(self):
        dict = {'id': self.id,
                'is_treat': self.is_treat,
                'name': self.name,
                'star_time': self.star_time,
                'end_time': self.end_time,
                'effect': self.effect,
                'is_family': self.is_family}
        return dict


# 家族史
class FamilyInfo(db.Model):
    __tablename__ = 'family_info'
    is_family = db.Column(db.String(50), nullable=True)
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    relationship = db.Column(db.String(50), nullable=True)
    diseases = db.Column(db.String(500), nullable=True)
    patient_id = db.Column(db.Integer(), db.ForeignKey('patient_info.id'))

    def to_dict(self):
        dict = {'is_family': self.is_family,
                'id': self.id,
                'relationship': self.relationship,
                'diseases': self.diseases}
        return dict

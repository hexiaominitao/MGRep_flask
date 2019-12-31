import json
from flask import jsonify
from flask_restful import (reqparse, Resource, fields, request)

from app.models import db
from app.models.qc import SampleQC, TableQC
from app.models.sample import SampleInfo


class Select2QC(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('qc_code', required=True,
                                 help='质控编号')
        self.parser.add_argument('targetKey', required=True,
                                 help='样本id')

    def get(self):
        return {'msg': 'hello'}, 200

    def post(self):
        args = self.parser.parse_args()
        qc_code = args.get('qc_code')
        targetKey = args.get('targetKey')
        qc = TableQC.query.filter(TableQC.name == qc_code).first()
        if qc:
            pass
        else:
            qc = TableQC(name=qc_code)
            db.session.add(qc)

        for id in json.loads(targetKey):
            print(id)
            sample = SampleInfo.query.filter(SampleInfo.id == 1).first()
            sample_qc = SampleQC(mg_id=sample.mg_id)
            db.session.add(sample_qc)
            sample.sample_qc.append(sample_qc)
            qc.sample_qc.append(sample_qc)
        # db.session.commit()

        return jsonify({'msg': 'hello'})


class DistillQC(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('')

    def get(self):
        pass

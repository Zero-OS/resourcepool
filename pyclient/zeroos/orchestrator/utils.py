import json


def Write_Status_code_Error(job, exception):
    service = job.service
    if 499 >= exception.code >= 400:
        job.model.dbobj.result = json.dumps({'message': exception.message, 'code': exception.code}).encode()
    service.saveAll()
    return

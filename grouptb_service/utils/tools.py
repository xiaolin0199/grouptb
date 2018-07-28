# -*- coding: utf-8 -*-

def response_dict(success=True, data=None, records=None, msg=None, errors=None):
    ret = {'success': success}
    if data is not None:
        ret['data'] = data
    if records is not None:
        ret['data'] = {'records': records}
    if msg:
        ret['msg'] = msg
    if errors:
        ret['errors'] = errors
    return ret

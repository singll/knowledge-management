"""统一响应格式"""
from flask import jsonify

def success(data=None, message='success', code=0):
    """成功响应"""
    return jsonify({
        'code': code,
        'message': message,
        'data': data
    }), 200

def error(message='error', code=-1, status_code=400):
    """错误响应"""
    return jsonify({
        'code': code,
        'message': message,
        'data': None
    }), status_code

def paginated_response(items, page, per_page, total):
    """分页响应"""
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': {
            'items': items,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }
    }), 200

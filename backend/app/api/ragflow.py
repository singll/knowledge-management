"""RagFlow API 路由"""
import logging
from flask import Blueprint, request
from app.services.ragflow_service import RagFlowService
from app.utils.response import success, error

bp = Blueprint('ragflow', __name__)
logger = logging.getLogger(__name__)

@bp.route('/upload/string', methods=['POST'])
def upload_string():
    """上传字符串内容"""
    try:
        data = request.get_json()
        if not data:
            return error('请求体必须是 JSON 格式', status_code=400)
        
        dataset_id = data.get('dataset_id')
        content = data.get('content')
        filename = data.get('filename', 'document.md')
        parser_id = data.get('parser_id', 'naive')
        run = data.get('run', '1')
        wait = data.get('wait_for_completion', False)
        
        if not dataset_id:
            return error('dataset_id 不能为空', status_code=400)
        if not content:
            return error('content 不能为空', status_code=400)
        
        service = RagFlowService()
        result = service.upload_string(
            dataset_id=dataset_id,
            content=content,
            filename=filename,
            parser_id=parser_id,
            run=run,
            wait=wait
        )
        
        return success(result, '上传成功')
        
    except Exception as e:
        logger.error(f"上传失败: {e}", exc_info=True)
        return error(f'上传失败: {str(e)}', status_code=500)


@bp.route('/documents', methods=['GET'])
def list_documents():
    """列出文档"""
    try:
        dataset_id = request.args.get('dataset_id')
        if not dataset_id:
            return error('dataset_id 不能为空', status_code=400)
        
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        keywords = request.args.get('keywords')
        
        service = RagFlowService()
        result = service.list_documents(dataset_id, page, page_size, keywords)
        
        return success(result)
        
    except Exception as e:
        logger.error(f"列出文档失败: {e}", exc_info=True)
        return error(f'列出文档失败: {str(e)}', status_code=500)


@bp.route('/documents/detail', methods=['GET'])
def get_document():
    """获取文档详情"""
    try:
        dataset_id = request.args.get('dataset_id')
        document_id = request.args.get('document_id')
        
        if not dataset_id or not document_id:
            return error('dataset_id 和 document_id 不能为空', status_code=400)
        
        service = RagFlowService()
        result = service.get_document(dataset_id, document_id)
        
        return success(result)
        
    except Exception as e:
        logger.error(f"获取文档失败: {e}", exc_info=True)
        return error(f'获取文档失败: {str(e)}', status_code=500)


@bp.route('/documents', methods=['DELETE'])
def delete_document():
    """删除文档"""
    try:
        data = request.get_json()
        dataset_id = data.get('dataset_id')
        document_id = data.get('document_id')
        
        if not dataset_id or not document_id:
            return error('dataset_id 和 document_id 不能为空', status_code=400)
        
        service = RagFlowService()
        result = service.delete_document(dataset_id, document_id)
        
        return success(result, '删除成功')
        
    except Exception as e:
        logger.error(f"删除文档失败: {e}", exc_info=True)
        return error(f'删除文档失败: {str(e)}', status_code=500)


@bp.route('/upload/batch', methods=['POST'])
def upload_batch():
    """批量上传字符串"""
    try:
        data = request.get_json()
        dataset_id = data.get('dataset_id')
        documents = data.get('documents', [])
        parser_id = data.get('parser_id', 'naive')
        run = data.get('run', '1')
        
        if not dataset_id:
            return error('dataset_id 不能为空', status_code=400)
        if not documents:
            return error('documents 不能为空', status_code=400)
        
        service = RagFlowService()
        results = []
        
        for doc in documents:
            try:
                result = service.upload_string(
                    dataset_id=dataset_id,
                    content=doc.get('content'),
                    filename=doc.get('filename', 'document.md'),
                    parser_id=parser_id,
                    run=run
                )
                results.append({
                    'success': True,
                    'filename': doc.get('filename'),
                    'document_id': result.get('document_id')
                })
            except Exception as e:
                results.append({
                    'success': False,
                    'filename': doc.get('filename'),
                    'error': str(e)
                })
        
        return success({'results': results}, '批量上传完成')
        
    except Exception as e:
        logger.error(f"批量上传失败: {e}", exc_info=True)
        return error(f'批量上传失败: {str(e)}', status_code=500)

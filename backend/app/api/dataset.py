"""Dataset (知识库) 管理 API"""
import logging
from flask import Blueprint, request
from app.services.ragflow_service import RagFlowService
from app.utils.response import success, error

bp = Blueprint('dataset', __name__)
logger = logging.getLogger(__name__)

@bp.route('/datasets', methods=['GET'])
def list_datasets():
    """获取知识库列表"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 30))
        name = request.args.get('name')
        orderby = request.args.get('orderby', 'create_time')
        desc = request.args.get('desc', 'true').lower() == 'true'
        
        service = RagFlowService()
        result = service.list_datasets(page, page_size, orderby, desc, name)
        
        return success(result.get('data', {}))
        
    except Exception as e:
        logger.error(f"获取知识库列表失败: {e}", exc_info=True)
        return error(f'获取知识库列表失败: {str(e)}', status_code=500)


@bp.route('/datasets/<dataset_id>', methods=['GET'])
def get_dataset(dataset_id):
    """获取知识库详情"""
    try:
        service = RagFlowService()
        result = service.get_dataset(dataset_id)
        
        return success(result.get('data', {}))
        
    except Exception as e:
        logger.error(f"获取知识库详情失败: {e}", exc_info=True)
        return error(f'获取知识库详情失败: {str(e)}', status_code=500)


@bp.route('/datasets', methods=['POST'])
def create_dataset():
    """创建知识库"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        
        if not name:
            return error('知识库名称不能为空', status_code=400)
        
        service = RagFlowService()
        result = service.create_dataset(
            name=name,
            avatar=data.get('avatar', ''),
            description=data.get('description', ''),
            language=data.get('language', 'English'),
            embedding_model=data.get('embedding_model', 'BAAI/bge-large-zh-v1.5'),
            permission=data.get('permission', 'me'),
            chunk_method=data.get('chunk_method', 'naive'),
            parser_config=data.get('parser_config')
        )
        
        return success(result.get('data', {}), '创建成功')
        
    except Exception as e:
        logger.error(f"创建知识库失败: {e}", exc_info=True)
        return error(f'创建知识库失败: {str(e)}', status_code=500)


@bp.route('/datasets/<dataset_id>', methods=['PUT'])
def update_dataset(dataset_id):
    """更新知识库"""
    try:
        data = request.get_json()
        
        service = RagFlowService()
        result = service.update_dataset(
            dataset_id=dataset_id,
            name=data.get('name'),
            description=data.get('description'),
            embedding_model=data.get('embedding_model'),
            chunk_method=data.get('chunk_method'),
            parser_config=data.get('parser_config')
        )
        
        return success(result.get('data', {}), '更新成功')
        
    except Exception as e:
        logger.error(f"更新知识库失败: {e}", exc_info=True)
        return error(f'更新知识库失败: {str(e)}', status_code=500)


@bp.route('/datasets/<dataset_id>', methods=['DELETE'])
def delete_dataset(dataset_id):
    """删除知识库"""
    try:
        service = RagFlowService()
        result = service.delete_dataset(dataset_id)
        
        return success(result.get('data', {}), '删除成功')
        
    except Exception as e:
        logger.error(f"删除知识库失败: {e}", exc_info=True)
        return error(f'删除知识库失败: {str(e)}', status_code=500)

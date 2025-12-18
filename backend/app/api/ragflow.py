"""RagFlow API 路由"""
import logging
from flask import Blueprint, request
from app.services.ragflow_service import RagFlowService
from app.utils.response import success, error

bp = Blueprint('ragflow', __name__)
logger = logging.getLogger(__name__)


# ============ 知识库（Dataset）管理 API ============

@bp.route('/datasets', methods=['GET'])
def list_datasets():
    """获取所有知识库列表"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 30))
        name = request.args.get('name')

        service = RagFlowService()
        result = service.list_datasets(page=page, page_size=page_size, name=name)

        return success(result)

    except Exception as e:
        logger.error(f"获取知识库列表失败: {e}", exc_info=True)
        return error(f'获取知识库列表失败: {str(e)}', status_code=500)


@bp.route('/datasets/<dataset_id>', methods=['GET'])
def get_dataset(dataset_id):
    """获取知识库详情"""
    try:
        service = RagFlowService()
        result = service.get_dataset(dataset_id)

        return success(result)

    except Exception as e:
        logger.error(f"获取知识库详情失败: {e}", exc_info=True)
        return error(f'获取知识库详情失败: {str(e)}', status_code=500)


@bp.route('/datasets', methods=['POST'])
def create_dataset():
    """创建知识库"""
    try:
        data = request.get_json()
        name = data.get('name')

        if not name:
            return error('知识库名称不能为空', status_code=400)

        service = RagFlowService()
        result = service.create_dataset(
            name=name,
            description=data.get('description', ''),
            language=data.get('language', 'Chinese'),
            embedding_model=data.get('embedding_model', 'BAAI/bge-large-zh-v1.5'),
            chunk_method=data.get('chunk_method', 'naive'),
            parser_config=data.get('parser_config')
        )

        return success(result, '创建成功')

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
            chunk_method=data.get('chunk_method'),
            parser_config=data.get('parser_config')
        )

        return success(result, '更新成功')

    except Exception as e:
        logger.error(f"更新知识库失败: {e}", exc_info=True)
        return error(f'更新知识库失败: {str(e)}', status_code=500)


@bp.route('/datasets/<dataset_id>', methods=['DELETE'])
def delete_dataset(dataset_id):
    """删除知识库"""
    try:
        service = RagFlowService()
        result = service.delete_dataset(dataset_id)

        return success(result, '删除成功')

    except Exception as e:
        logger.error(f"删除知识库失败: {e}", exc_info=True)
        return error(f'删除知识库失败: {str(e)}', status_code=500)


# ============ 文档管理 API ============

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


@bp.route('/upload/with-tags', methods=['POST'])
def upload_with_tags():
    """上传文档并自动处理标签

    请求体:
    {
        "dataset_id": "xxx",  // 可选，如果不提供则根据标签自动选择
        "content": "文档内容",
        "filename": "document.md",
        "title": "文章标题",
        "url": "文章原始URL",
        "tags": ["标签1", "标签2"],  // 从文章提取的标签
        "keywords": ["关键词1", "关键词2"],  // 用于匹配现有标签
        "category": "security",  // 分类，用于备选知识库选择
        "auto_create_tags": true,  // 是否自动创建不存在的标签
        "parser_id": "naive",
        "run": "1"
    }
    """
    try:
        from app.models import DatasetMapping, Tag, ArticleTag
        from app.extensions import db

        data = request.get_json()
        if not data:
            return error('请求体必须是 JSON 格式', status_code=400)

        content = data.get('content')
        if not content:
            return error('content 不能为空', status_code=400)

        filename = data.get('filename', 'document.md')
        title = data.get('title', '')
        url = data.get('url', '')
        input_tags = data.get('tags', [])
        keywords = data.get('keywords', [])
        category = data.get('category', '')
        auto_create_tags = data.get('auto_create_tags', True)
        parser_id = data.get('parser_id', 'naive')
        run = data.get('run', '1')
        dataset_id = data.get('dataset_id')

        # 1. 处理标签：合并输入标签和关键词匹配的标签
        all_tag_names = list(set(input_tags))

        # 根据关键词匹配现有标签
        if keywords:
            existing_tags = Tag.query.all()
            for keyword in keywords:
                keyword_lower = keyword.lower().strip()
                for tag in existing_tags:
                    if tag.name.lower() == keyword_lower or \
                       keyword_lower in tag.name.lower() or \
                       tag.name.lower() in keyword_lower:
                        if tag.name not in all_tag_names:
                            all_tag_names.append(tag.name)

        # 2. 获取或创建标签
        final_tags = []
        for name in all_tag_names:
            name = name.strip()
            if not name:
                continue
            tag = Tag.query.filter_by(name=name).first()
            if not tag and auto_create_tags:
                tag = Tag(name=name, description='自动创建的标签', color='#909399')
                db.session.add(tag)
                db.session.flush()
            if tag:
                final_tags.append(tag)

        # 3. 确定目标知识库
        if not dataset_id:
            # 根据标签匹配知识库
            if final_tags:
                tag_ids = [t.id for t in final_tags]
                mappings = DatasetMapping.query.filter(
                    DatasetMapping.is_active == True,
                    DatasetMapping.tags.any(Tag.id.in_(tag_ids))
                ).all()

                if mappings:
                    # 选择匹配度最高的
                    best_match = max(mappings, key=lambda m: len([t for t in m.tags if t.id in tag_ids]))
                    dataset_id = best_match.dataset_id
                    parser_id = best_match.parser_id or parser_id

            # 如果标签匹配失败，尝试按分类
            if not dataset_id and category:
                mapping = DatasetMapping.query.filter_by(name=category, is_active=True).first()
                if mapping:
                    dataset_id = mapping.dataset_id
                    parser_id = mapping.parser_id or parser_id

            # 使用默认知识库
            if not dataset_id:
                default_mapping = DatasetMapping.query.filter_by(is_default=True, is_active=True).first()
                if default_mapping:
                    dataset_id = default_mapping.dataset_id
                    parser_id = default_mapping.parser_id or parser_id

            if not dataset_id:
                return error('无法确定目标知识库，请提供 dataset_id 或配置知识库映射', status_code=400)

        # 4. 上传文档到 RagFlow
        service = RagFlowService()
        result = service.upload_string(
            dataset_id=dataset_id,
            content=content,
            filename=filename,
            parser_id=parser_id,
            run=run
        )

        document_id = result.get('document_id')

        # 5. 创建文章-标签关联
        if document_id and final_tags:
            for tag in final_tags:
                article_tag = ArticleTag(
                    document_id=document_id,
                    dataset_id=dataset_id,
                    tag_id=tag.id,
                    article_title=title,
                    article_url=url
                )
                db.session.add(article_tag)

        db.session.commit()

        return success({
            'document_id': document_id,
            'dataset_id': dataset_id,
            'tags': [t.to_dict() for t in final_tags],
            'filename': filename
        }, '上传成功')

    except Exception as e:
        db.session.rollback()
        logger.error(f"上传文档失败: {e}", exc_info=True)
        return error(f'上传文档失败: {str(e)}', status_code=500)

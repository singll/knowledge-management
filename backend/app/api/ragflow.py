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

        # 5. 更新文档元数据（将 URL 存入 RagFlow，用于去重）
        if document_id and url:
            try:
                meta_fields = {
                    'source_url': url,
                    'title': title,
                    'tags': [t.name for t in final_tags],
                    'crawl_time': data.get('crawl_time', ''),
                    'category': category
                }
                service.update_document_metadata(dataset_id, document_id, meta_fields)
                logger.info(f"文档元数据已更新: doc={document_id}, url={url}")
            except Exception as meta_err:
                logger.warning(f"更新文档元数据失败（不影响上传）: {meta_err}")

        # 6. 创建文章-标签关联（保留用于向后兼容，但主要依赖 RagFlow 元数据）
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
            'filename': filename,
            'metadata_stored': bool(url)
        }, '上传成功')

    except Exception as e:
        db.session.rollback()
        logger.error(f"上传文档失败: {e}", exc_info=True)
        return error(f'上传文档失败: {str(e)}', status_code=500)


# ============ 文档解析 API ============

@bp.route('/documents/parse', methods=['POST'])
def run_parsing():
    """触发文档解析

    请求体:
    {
        "dataset_id": "xxx",
        "document_ids": ["doc1", "doc2"]
    }
    """
    try:
        data = request.get_json()
        dataset_id = data.get('dataset_id')
        document_ids = data.get('document_ids', [])

        if not dataset_id:
            return error('dataset_id 不能为空', status_code=400)
        if not document_ids:
            return error('document_ids 不能为空', status_code=400)

        service = RagFlowService()
        result = service.run_parsing(dataset_id, document_ids)

        return success(result, '已触发解析')

    except Exception as e:
        logger.error(f"触发解析失败: {e}", exc_info=True)
        return error(f'触发解析失败: {str(e)}', status_code=500)


@bp.route('/documents/parse/stop', methods=['POST'])
def stop_parsing():
    """停止文档解析

    请求体:
    {
        "dataset_id": "xxx",
        "document_ids": ["doc1", "doc2"]
    }
    """
    try:
        data = request.get_json()
        dataset_id = data.get('dataset_id')
        document_ids = data.get('document_ids', [])

        if not dataset_id:
            return error('dataset_id 不能为空', status_code=400)
        if not document_ids:
            return error('document_ids 不能为空', status_code=400)

        service = RagFlowService()
        result = service.stop_parsing(dataset_id, document_ids)

        return success(result, '已停止解析')

    except Exception as e:
        logger.error(f"停止解析失败: {e}", exc_info=True)
        return error(f'停止解析失败: {str(e)}', status_code=500)


@bp.route('/documents/parse/status', methods=['GET'])
def get_parsing_status():
    """获取文档解析状态"""
    try:
        dataset_id = request.args.get('dataset_id')
        document_id = request.args.get('document_id')

        if not dataset_id or not document_id:
            return error('dataset_id 和 document_id 不能为空', status_code=400)

        service = RagFlowService()
        result = service.get_parsing_status(dataset_id, document_id)

        return success(result)

    except Exception as e:
        logger.error(f"获取解析状态失败: {e}", exc_info=True)
        return error(f'获取解析状态失败: {str(e)}', status_code=500)


# ============ 批量操作 API ============

@bp.route('/documents/batch-delete', methods=['POST'])
def batch_delete_documents():
    """批量删除文档

    请求体:
    {
        "dataset_id": "xxx",
        "document_ids": ["doc1", "doc2"]
    }
    """
    try:
        from app.models import ArticleTag
        from app.extensions import db

        data = request.get_json()
        dataset_id = data.get('dataset_id')
        document_ids = data.get('document_ids', [])

        if not dataset_id:
            return error('dataset_id 不能为空', status_code=400)
        if not document_ids:
            return error('document_ids 不能为空', status_code=400)

        service = RagFlowService()
        result = service.delete_documents_batch(dataset_id, document_ids)

        # 同时删除本地的文章标签关联
        ArticleTag.query.filter(
            ArticleTag.dataset_id == dataset_id,
            ArticleTag.document_id.in_(document_ids)
        ).delete(synchronize_session=False)
        db.session.commit()

        return success({
            'ragflow_result': result,
            'deleted_count': len(document_ids)
        }, '批量删除成功')

    except Exception as e:
        db.session.rollback()
        logger.error(f"批量删除失败: {e}", exc_info=True)
        return error(f'批量删除失败: {str(e)}', status_code=500)


@bp.route('/documents/transfer', methods=['POST'])
def transfer_document():
    """转移单个文档到另一个知识库

    请求体:
    {
        "source_dataset_id": "xxx",
        "target_dataset_id": "yyy",
        "document_id": "doc1",
        "delete_source": true,
        "parser_id": "naive",
        "run": "1"
    }
    """
    try:
        from app.models import ArticleTag
        from app.extensions import db

        data = request.get_json()
        source_dataset_id = data.get('source_dataset_id')
        target_dataset_id = data.get('target_dataset_id')
        document_id = data.get('document_id')
        delete_source = data.get('delete_source', True)
        parser_id = data.get('parser_id', 'naive')
        run = data.get('run', '1')

        if not source_dataset_id or not target_dataset_id:
            return error('source_dataset_id 和 target_dataset_id 不能为空', status_code=400)
        if not document_id:
            return error('document_id 不能为空', status_code=400)
        if source_dataset_id == target_dataset_id:
            return error('源知识库和目标知识库不能相同', status_code=400)

        service = RagFlowService()
        result = service.transfer_document(
            source_dataset_id, target_dataset_id, document_id,
            delete_source=delete_source, parser_id=parser_id, run=run
        )

        # 更新本地文章标签关联
        if result.get('success') and result.get('target_document_id'):
            ArticleTag.query.filter_by(
                dataset_id=source_dataset_id,
                document_id=document_id
            ).update({
                'dataset_id': target_dataset_id,
                'document_id': result['target_document_id']
            })
            db.session.commit()

        return success(result, '文档转移成功')

    except Exception as e:
        db.session.rollback()
        logger.error(f"文档转移失败: {e}", exc_info=True)
        return error(f'文档转移失败: {str(e)}', status_code=500)


@bp.route('/documents/batch-transfer', methods=['POST'])
def batch_transfer_documents():
    """批量转移文档到另一个知识库

    请求体:
    {
        "source_dataset_id": "xxx",
        "target_dataset_id": "yyy",
        "document_ids": ["doc1", "doc2"],
        "delete_source": true,
        "parser_id": "naive",
        "run": "1"
    }
    """
    try:
        from app.models import ArticleTag
        from app.extensions import db

        data = request.get_json()
        source_dataset_id = data.get('source_dataset_id')
        target_dataset_id = data.get('target_dataset_id')
        document_ids = data.get('document_ids', [])
        delete_source = data.get('delete_source', True)
        parser_id = data.get('parser_id', 'naive')
        run = data.get('run', '1')

        if not source_dataset_id or not target_dataset_id:
            return error('source_dataset_id 和 target_dataset_id 不能为空', status_code=400)
        if not document_ids:
            return error('document_ids 不能为空', status_code=400)
        if source_dataset_id == target_dataset_id:
            return error('源知识库和目标知识库不能相同', status_code=400)

        service = RagFlowService()
        result = service.transfer_documents_batch(
            source_dataset_id, target_dataset_id, document_ids,
            delete_source=delete_source, parser_id=parser_id, run=run
        )

        # 更新本地文章标签关联
        for item in result.get('results', []):
            if item.get('success') and item.get('target_document_id'):
                ArticleTag.query.filter_by(
                    dataset_id=source_dataset_id,
                    document_id=item['source_document_id']
                ).update({
                    'dataset_id': target_dataset_id,
                    'document_id': item['target_document_id']
                })
        db.session.commit()

        return success(result, '批量转移完成')

    except Exception as e:
        db.session.rollback()
        logger.error(f"批量转移失败: {e}", exc_info=True)
        return error(f'批量转移失败: {str(e)}', status_code=500)


# ============ Chunk (分块) 管理 API ============

@bp.route('/chunks', methods=['GET'])
def list_chunks():
    """列出文档分块"""
    try:
        dataset_id = request.args.get('dataset_id')
        document_id = request.args.get('document_id')

        if not dataset_id or not document_id:
            return error('dataset_id 和 document_id 不能为空', status_code=400)

        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        keywords = request.args.get('keywords')

        service = RagFlowService()
        result = service.list_chunks(dataset_id, document_id, page, page_size, keywords)

        return success(result)

    except Exception as e:
        logger.error(f"获取分块列表失败: {e}", exc_info=True)
        return error(f'获取分块列表失败: {str(e)}', status_code=500)


@bp.route('/chunks', methods=['DELETE'])
def delete_chunks():
    """删除指定分块

    请求体:
    {
        "dataset_id": "xxx",
        "document_id": "yyy",
        "chunk_ids": ["chunk1", "chunk2"]
    }
    """
    try:
        data = request.get_json()
        dataset_id = data.get('dataset_id')
        document_id = data.get('document_id')
        chunk_ids = data.get('chunk_ids', [])

        if not dataset_id or not document_id:
            return error('dataset_id 和 document_id 不能为空', status_code=400)
        if not chunk_ids:
            return error('chunk_ids 不能为空', status_code=400)

        service = RagFlowService()
        result = service.delete_chunks(dataset_id, document_id, chunk_ids)

        return success(result, '删除分块成功')

    except Exception as e:
        logger.error(f"删除分块失败: {e}", exc_info=True)
        return error(f'删除分块失败: {str(e)}', status_code=500)


# ============ 文档元数据 API ============

@bp.route('/documents/metadata', methods=['PUT'])
def update_document_metadata():
    """更新文档元数据

    请求体:
    {
        "dataset_id": "xxx",
        "document_id": "yyy",
        "meta_fields": {
            "source_url": "https://example.com/article",
            "author": "作者名",
            "tags": ["tag1", "tag2"]
        }
    }
    """
    try:
        data = request.get_json()
        dataset_id = data.get('dataset_id')
        document_id = data.get('document_id')
        meta_fields = data.get('meta_fields', {})

        if not dataset_id or not document_id:
            return error('dataset_id 和 document_id 不能为空', status_code=400)
        if not meta_fields:
            return error('meta_fields 不能为空', status_code=400)

        service = RagFlowService()
        result = service.update_document_metadata(dataset_id, document_id, meta_fields)

        return success(result, '更新元数据成功')

    except Exception as e:
        logger.error(f"更新元数据失败: {e}", exc_info=True)
        return error(f'更新元数据失败: {str(e)}', status_code=500)


@bp.route('/check-url', methods=['POST'])
def check_url_exists_in_ragflow():
    """检查 URL 是否已存在于 RagFlow 中

    通过搜索文档元数据中的 source_url 字段来检查，实现与 RagFlow 解耦的去重

    请求体:
    {
        "url": "https://example.com/article",
        "urls": ["url1", "url2"],  // 批量检查时使用
        "dataset_ids": ["id1", "id2"]  // 可选，指定搜索的知识库
    }

    返回:
    单个 URL: {"exists": true/false, "document_id": "xxx", "dataset_id": "xxx", "match_type": "exact/normalized"}
    批量 URL: {"results": {"url1": {...}, "url2": {...}}}
    """
    try:
        data = request.get_json()
        single_url = data.get('url')
        urls = data.get('urls', [])
        dataset_ids = data.get('dataset_ids')

        service = RagFlowService()

        if single_url:
            # 单个 URL 检查
            result = service.check_url_in_ragflow(single_url, dataset_ids)
            return success(result)

        elif urls:
            # 批量 URL 检查
            results = service.batch_check_urls_in_ragflow(urls, dataset_ids)
            return success({'results': results})

        else:
            return error('url 或 urls 参数不能为空', status_code=400)

    except Exception as e:
        logger.error(f"检查 URL 是否存在失败: {e}", exc_info=True)
        return error(f'检查 URL 是否存在失败: {str(e)}', status_code=500)

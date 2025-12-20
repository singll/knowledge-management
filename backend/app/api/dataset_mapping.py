"""知识库映射 API"""
import logging
from flask import Blueprint, request
from app.models import DatasetMapping, Tag, ArticleTag
from app.extensions import db
from app.utils.response import success, error, paginated_response

bp = Blueprint('dataset_mapping', __name__)
logger = logging.getLogger(__name__)


@bp.route('', methods=['GET'])
def list_mappings():
    """获取知识库映射列表"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        keyword = request.args.get('keyword', '').strip()
        is_active = request.args.get('is_active')

        query = DatasetMapping.query

        if keyword:
            query = query.filter(
                db.or_(
                    DatasetMapping.name.contains(keyword),
                    DatasetMapping.display_name.contains(keyword)
                )
            )

        if is_active is not None:
            query = query.filter(DatasetMapping.is_active == (is_active.lower() == 'true'))

        pagination = query.order_by(DatasetMapping.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        items = [mapping.to_dict() for mapping in pagination.items]
        return paginated_response(items, page, per_page, pagination.total)

    except Exception as e:
        logger.error(f"获取知识库映射列表失败: {e}", exc_info=True)
        return error(f'获取知识库映射列表失败: {str(e)}', status_code=500)


@bp.route('/all', methods=['GET'])
def get_all_mappings():
    """获取所有活跃的知识库映射（不分页，供工作流使用）"""
    try:
        mappings = DatasetMapping.query.filter_by(is_active=True).order_by(DatasetMapping.name).all()

        # 构建简化的映射字典，方便工作流使用
        mapping_dict = {}
        for m in mappings:
            mapping_dict[m.name] = {
                'dataset_id': m.dataset_id,
                'display_name': m.display_name,
                'parser_id': m.parser_id,
                'tags': [t.name for t in m.tags]
            }

        return success({
            'mappings': mapping_dict,
            'list': [m.to_dict() for m in mappings]
        })

    except Exception as e:
        logger.error(f"获取所有知识库映射失败: {e}", exc_info=True)
        return error(f'获取所有知识库映射失败: {str(e)}', status_code=500)


@bp.route('/by-name/<name>', methods=['GET'])
def get_mapping_by_name(name):
    """根据名称获取知识库映射"""
    try:
        mapping = DatasetMapping.query.filter_by(name=name).first()
        if not mapping:
            return error('知识库映射不存在', status_code=404)

        return success(mapping.to_dict())

    except Exception as e:
        logger.error(f"获取知识库映射失败: {e}", exc_info=True)
        return error(f'获取知识库映射失败: {str(e)}', status_code=500)


@bp.route('/by-tag', methods=['POST'])
def get_mapping_by_tag():
    """根据标签获取推荐的知识库

    请求体:
    {
        "tags": ["标签1", "标签2"],
        "category": "security"  // 可选，作为备选
    }
    """
    try:
        data = request.get_json()
        tag_names = data.get('tags', [])
        category = data.get('category', '')

        # 优先根据标签匹配知识库
        if tag_names:
            # 查找关联了这些标签的知识库
            tags = Tag.query.filter(Tag.name.in_(tag_names)).all()
            tag_ids = [t.id for t in tags]

            if tag_ids:
                # 查找关联了这些标签的知识库映射
                mappings = DatasetMapping.query.filter(
                    DatasetMapping.is_active == True,
                    DatasetMapping.tags.any(Tag.id.in_(tag_ids))
                ).all()

                if mappings:
                    # 返回匹配度最高的知识库（关联标签最多的）
                    best_match = max(mappings, key=lambda m: len([t for t in m.tags if t.id in tag_ids]))
                    return success({
                        'mapping': best_match.to_dict(),
                        'match_type': 'tag',
                        'matched_tags': [t.name for t in best_match.tags if t.id in tag_ids]
                    })

        # 如果标签匹配失败，尝试按分类查找
        if category:
            mapping = DatasetMapping.query.filter_by(name=category, is_active=True).first()
            if mapping:
                return success({
                    'mapping': mapping.to_dict(),
                    'match_type': 'category'
                })

        # 返回默认知识库
        default_mapping = DatasetMapping.query.filter_by(is_default=True, is_active=True).first()
        if default_mapping:
            return success({
                'mapping': default_mapping.to_dict(),
                'match_type': 'default'
            })

        # 如果没有默认知识库，返回第一个活跃的
        first_mapping = DatasetMapping.query.filter_by(is_active=True).first()
        if first_mapping:
            return success({
                'mapping': first_mapping.to_dict(),
                'match_type': 'fallback'
            })

        return error('没有可用的知识库映射', status_code=404)

    except Exception as e:
        logger.error(f"根据标签获取知识库映射失败: {e}", exc_info=True)
        return error(f'根据标签获取知识库映射失败: {str(e)}', status_code=500)


@bp.route('/<int:mapping_id>', methods=['GET'])
def get_mapping(mapping_id):
    """获取单个知识库映射"""
    try:
        mapping = DatasetMapping.query.get(mapping_id)
        if not mapping:
            return error('知识库映射不存在', status_code=404)

        return success(mapping.to_dict())

    except Exception as e:
        logger.error(f"获取知识库映射失败: {e}", exc_info=True)
        return error(f'获取知识库映射失败: {str(e)}', status_code=500)


@bp.route('', methods=['POST'])
def create_mapping():
    """创建知识库映射"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        dataset_id = data.get('dataset_id', '').strip()

        if not name:
            return error('映射名称不能为空', status_code=400)
        if not dataset_id:
            return error('Dataset ID 不能为空', status_code=400)

        # 检查是否已存在
        existing = DatasetMapping.query.filter_by(name=name).first()
        if existing:
            return error('映射名称已存在', status_code=400)

        mapping = DatasetMapping(
            name=name,
            display_name=data.get('display_name', name),
            dataset_id=dataset_id,
            description=data.get('description', ''),
            is_default=data.get('is_default', False),
            is_active=data.get('is_active', True),
            parser_id=data.get('parser_id', 'naive')
        )

        # 处理标签关联
        tag_ids = data.get('tag_ids', [])
        if tag_ids:
            tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
            mapping.tags = tags

        # 如果设为默认，取消其他默认
        if mapping.is_default:
            DatasetMapping.query.filter(DatasetMapping.id != mapping.id).update({'is_default': False})

        db.session.add(mapping)
        db.session.commit()

        return success(mapping.to_dict(), '创建成功')

    except Exception as e:
        db.session.rollback()
        logger.error(f"创建知识库映射失败: {e}", exc_info=True)
        return error(f'创建知识库映射失败: {str(e)}', status_code=500)


@bp.route('/<int:mapping_id>', methods=['PUT'])
def update_mapping(mapping_id):
    """更新知识库映射"""
    try:
        mapping = DatasetMapping.query.get(mapping_id)
        if not mapping:
            return error('知识库映射不存在', status_code=404)

        data = request.get_json()

        if 'name' in data:
            name = data['name'].strip()
            if not name:
                return error('映射名称不能为空', status_code=400)
            # 检查名称是否重复
            existing = DatasetMapping.query.filter(
                DatasetMapping.name == name,
                DatasetMapping.id != mapping_id
            ).first()
            if existing:
                return error('映射名称已存在', status_code=400)
            mapping.name = name

        if 'display_name' in data:
            mapping.display_name = data['display_name']

        if 'dataset_id' in data:
            dataset_id = data['dataset_id'].strip()
            if not dataset_id:
                return error('Dataset ID 不能为空', status_code=400)
            mapping.dataset_id = dataset_id

        if 'description' in data:
            mapping.description = data['description']

        if 'is_default' in data:
            mapping.is_default = data['is_default']
            # 如果设为默认，取消其他默认
            if mapping.is_default:
                DatasetMapping.query.filter(DatasetMapping.id != mapping_id).update({'is_default': False})

        if 'is_active' in data:
            mapping.is_active = data['is_active']

        if 'parser_id' in data:
            mapping.parser_id = data['parser_id']

        # 处理标签关联
        if 'tag_ids' in data:
            tag_ids = data['tag_ids']
            tags = Tag.query.filter(Tag.id.in_(tag_ids)).all() if tag_ids else []
            mapping.tags = tags

        db.session.commit()

        return success(mapping.to_dict(), '更新成功')

    except Exception as e:
        db.session.rollback()
        logger.error(f"更新知识库映射失败: {e}", exc_info=True)
        return error(f'更新知识库映射失败: {str(e)}', status_code=500)


@bp.route('/<int:mapping_id>', methods=['DELETE'])
def delete_mapping(mapping_id):
    """删除知识库映射"""
    try:
        mapping = DatasetMapping.query.get(mapping_id)
        if not mapping:
            return error('知识库映射不存在', status_code=404)

        db.session.delete(mapping)
        db.session.commit()

        return success(None, '删除成功')

    except Exception as e:
        db.session.rollback()
        logger.error(f"删除知识库映射失败: {e}", exc_info=True)
        return error(f'删除知识库映射失败: {str(e)}', status_code=500)


# ============ 文章标签关联 API ============

@bp.route('/article-tags', methods=['POST'])
def add_article_tags():
    """为文章添加标签关联

    请求体:
    {
        "document_id": "xxx",
        "dataset_id": "xxx",
        "tag_ids": [1, 2, 3],
        "tag_names": ["标签1", "标签2"],  // 可选，如果提供会自动创建不存在的标签
        "article_title": "文章标题",
        "article_url": "文章URL"
    }
    """
    try:
        data = request.get_json()
        document_id = data.get('document_id')
        dataset_id = data.get('dataset_id')

        if not document_id or not dataset_id:
            return error('document_id 和 dataset_id 不能为空', status_code=400)

        tag_ids = data.get('tag_ids', [])
        tag_names = data.get('tag_names', [])
        article_title = data.get('article_title', '')
        article_url = data.get('article_url', '')

        # 处理 tag_names，自动创建不存在的标签
        if tag_names:
            for name in tag_names:
                name = name.strip()
                if not name:
                    continue
                tag = Tag.query.filter_by(name=name).first()
                if not tag:
                    tag = Tag(name=name, description='自动创建的标签', color='#909399')
                    db.session.add(tag)
                    db.session.flush()
                if tag.id not in tag_ids:
                    tag_ids.append(tag.id)

        # 删除旧的关联
        ArticleTag.query.filter_by(document_id=document_id, dataset_id=dataset_id).delete()

        # 创建新的关联
        created = []
        for tag_id in tag_ids:
            article_tag = ArticleTag(
                document_id=document_id,
                dataset_id=dataset_id,
                tag_id=tag_id,
                article_title=article_title,
                article_url=article_url
            )
            db.session.add(article_tag)
            created.append(article_tag)

        db.session.commit()

        return success({
            'count': len(created),
            'tags': [at.to_dict() for at in created]
        }, '标签关联成功')

    except Exception as e:
        db.session.rollback()
        logger.error(f"添加文章标签关联失败: {e}", exc_info=True)
        return error(f'添加文章标签关联失败: {str(e)}', status_code=500)


@bp.route('/article-tags/<document_id>', methods=['GET'])
def get_article_tags(document_id):
    """获取文章的标签"""
    try:
        dataset_id = request.args.get('dataset_id')

        query = ArticleTag.query.filter_by(document_id=document_id)
        if dataset_id:
            query = query.filter_by(dataset_id=dataset_id)

        article_tags = query.all()

        return success({
            'document_id': document_id,
            'tags': [at.to_dict() for at in article_tags]
        })

    except Exception as e:
        logger.error(f"获取文章标签失败: {e}", exc_info=True)
        return error(f'获取文章标签失败: {str(e)}', status_code=500)


@bp.route('/articles-by-tag/<int:tag_id>', methods=['GET'])
def get_articles_by_tag(tag_id):
    """根据标签获取文章列表"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        dataset_id = request.args.get('dataset_id')

        query = ArticleTag.query.filter_by(tag_id=tag_id)
        if dataset_id:
            query = query.filter_by(dataset_id=dataset_id)

        pagination = query.order_by(ArticleTag.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        items = [at.to_dict() for at in pagination.items]
        return paginated_response(items, page, per_page, pagination.total)

    except Exception as e:
        logger.error(f"根据标签获取文章列表失败: {e}", exc_info=True)
        return error(f'根据标签获取文章列表失败: {str(e)}', status_code=500)


def normalize_url(url):
    """规范化 URL 用于比较

    - 移除末尾斜杠
    - 统一小写域名
    - 移除常见追踪参数
    """
    if not url:
        return url

    from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

    url = url.strip()

    # 解析 URL
    parsed = urlparse(url)

    # 小写域名
    netloc = parsed.netloc.lower()

    # 移除末尾斜杠
    path = parsed.path.rstrip('/')

    # 移除常见追踪参数
    tracking_params = {'utm_source', 'utm_medium', 'utm_campaign', 'utm_term',
                      'utm_content', 'fbclid', 'gclid', 'ref', 'source'}
    if parsed.query:
        params = parse_qs(parsed.query)
        filtered_params = {k: v for k, v in params.items() if k.lower() not in tracking_params}
        query = urlencode(filtered_params, doseq=True) if filtered_params else ''
    else:
        query = ''

    # 重建 URL
    normalized = urlunparse((
        parsed.scheme,
        netloc,
        path,
        parsed.params,
        query,
        ''  # 移除 fragment
    ))

    return normalized


@bp.route('/check-url', methods=['POST'])
def check_url_exists():
    """检查 URL 是否已入库

    请求体:
    {
        "url": "https://example.com/article",
        "urls": ["url1", "url2"],  // 批量检查时使用
        "normalize": true,  // 是否规范化 URL 进行比较（默认 true）
        "fuzzy": false  // 是否模糊匹配（检查 URL 是否包含在已存储的 URL 中）
    }

    返回:
    单个 URL: {"exists": true/false, "document_id": "xxx", "dataset_id": "xxx"}
    批量 URL: {"results": {"url1": {"exists": true, ...}, "url2": {"exists": false}}}
    """
    try:
        data = request.get_json()
        single_url = data.get('url')
        urls = data.get('urls', [])
        should_normalize = data.get('normalize', True)
        fuzzy_match = data.get('fuzzy', False)

        if single_url:
            # 单个 URL 检查
            check_url = normalize_url(single_url) if should_normalize else single_url

            # 精确匹配
            article = ArticleTag.query.filter_by(article_url=single_url).first()

            # 如果精确匹配失败，尝试规范化匹配
            if not article and should_normalize:
                # 获取所有文章 URL 进行规范化比较
                all_articles = ArticleTag.query.filter(
                    ArticleTag.article_url.isnot(None)
                ).all()

                for a in all_articles:
                    if a.article_url and normalize_url(a.article_url) == check_url:
                        article = a
                        break

            # 如果还是没找到，尝试模糊匹配
            if not article and fuzzy_match:
                # 提取 URL 的路径部分进行模糊匹配
                from urllib.parse import urlparse
                parsed = urlparse(single_url)
                path_part = parsed.path.rstrip('/')

                if path_part and len(path_part) > 10:  # 确保路径足够长
                    article = ArticleTag.query.filter(
                        ArticleTag.article_url.contains(path_part)
                    ).first()

            if article:
                return success({
                    'exists': True,
                    'document_id': article.document_id,
                    'dataset_id': article.dataset_id,
                    'title': article.article_title,
                    'stored_url': article.article_url,
                    'created_at': article.created_at.isoformat() if article.created_at else None
                })
            else:
                return success({'exists': False})

        elif urls:
            # 批量 URL 检查
            results = {}

            # 获取所有相关的文章记录
            all_articles = ArticleTag.query.filter(
                ArticleTag.article_url.in_(urls)
            ).all()

            # 构建精确匹配的 URL 映射
            exact_map = {a.article_url: a for a in all_articles}

            # 如果需要规范化匹配，获取更多文章进行比较
            normalized_map = {}
            if should_normalize:
                # 获取所有有 URL 的文章
                all_url_articles = ArticleTag.query.filter(
                    ArticleTag.article_url.isnot(None)
                ).all()
                for a in all_url_articles:
                    if a.article_url:
                        norm_url = normalize_url(a.article_url)
                        if norm_url not in normalized_map:
                            normalized_map[norm_url] = a

            for url in urls:
                # 精确匹配
                if url in exact_map:
                    article = exact_map[url]
                    results[url] = {
                        'exists': True,
                        'document_id': article.document_id,
                        'dataset_id': article.dataset_id,
                        'match_type': 'exact'
                    }
                # 规范化匹配
                elif should_normalize:
                    norm_url = normalize_url(url)
                    if norm_url in normalized_map:
                        article = normalized_map[norm_url]
                        results[url] = {
                            'exists': True,
                            'document_id': article.document_id,
                            'dataset_id': article.dataset_id,
                            'match_type': 'normalized'
                        }
                    else:
                        results[url] = {'exists': False}
                else:
                    results[url] = {'exists': False}

            return success({'results': results})

        else:
            return error('url 或 urls 参数不能为空', status_code=400)

    except Exception as e:
        logger.error(f"检查 URL 是否存在失败: {e}", exc_info=True)
        return error(f'检查 URL 是否存在失败: {str(e)}', status_code=500)

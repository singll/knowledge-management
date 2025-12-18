"""标签管理 API"""
import logging
from flask import Blueprint, request
from app.models import Tag
from app.extensions import db
from app.utils.response import success, error, paginated_response

bp = Blueprint('tags', __name__)
logger = logging.getLogger(__name__)

@bp.route('', methods=['GET'])
def list_tags():
    """获取标签列表"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        keyword = request.args.get('keyword', '').strip()
        
        query = Tag.query
        if keyword:
            query = query.filter(Tag.name.contains(keyword))
        
        pagination = query.order_by(Tag.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        items = [tag.to_dict() for tag in pagination.items]
        return paginated_response(items, page, per_page, pagination.total)
        
    except Exception as e:
        logger.error(f"获取标签列表失败: {e}", exc_info=True)
        return error(f'获取标签列表失败: {str(e)}', status_code=500)


@bp.route('/<int:tag_id>', methods=['GET'])
def get_tag(tag_id):
    """获取单个标签"""
    try:
        tag = Tag.query.get(tag_id)
        if not tag:
            return error('标签不存在', status_code=404)
        
        return success(tag.to_dict())
        
    except Exception as e:
        logger.error(f"获取标签失败: {e}", exc_info=True)
        return error(f'获取标签失败: {str(e)}', status_code=500)


@bp.route('', methods=['POST'])
def create_tag():
    """创建标签"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        
        if not name:
            return error('标签名称不能为空', status_code=400)
        
        # 检查是否已存在
        existing = Tag.query.filter_by(name=name).first()
        if existing:
            return error('标签已存在', status_code=400)
        
        tag = Tag(
            name=name,
            description=data.get('description', '').strip(),
            color=data.get('color', '#409EFF')
        )
        
        db.session.add(tag)
        db.session.commit()
        
        return success(tag.to_dict(), '创建成功')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建标签失败: {e}", exc_info=True)
        return error(f'创建标签失败: {str(e)}', status_code=500)


@bp.route('/<int:tag_id>', methods=['PUT'])
def update_tag(tag_id):
    """更新标签"""
    try:
        tag = Tag.query.get(tag_id)
        if not tag:
            return error('标签不存在', status_code=404)
        
        data = request.get_json()
        
        if 'name' in data:
            name = data['name'].strip()
            if not name:
                return error('标签名称不能为空', status_code=400)
            # 检查名称是否重复
            existing = Tag.query.filter(Tag.name == name, Tag.id != tag_id).first()
            if existing:
                return error('标签名称已存在', status_code=400)
            tag.name = name
        
        if 'description' in data:
            tag.description = data['description'].strip()
        
        if 'color' in data:
            tag.color = data['color']
        
        db.session.commit()
        
        return success(tag.to_dict(), '更新成功')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新标签失败: {e}", exc_info=True)
        return error(f'更新标签失败: {str(e)}', status_code=500)


@bp.route('/<int:tag_id>', methods=['DELETE'])
def delete_tag(tag_id):
    """删除标签"""
    try:
        tag = Tag.query.get(tag_id)
        if not tag:
            return error('标签不存在', status_code=404)

        db.session.delete(tag)
        db.session.commit()

        return success(None, '删除成功')

    except Exception as e:
        db.session.rollback()
        logger.error(f"删除标签失败: {e}", exc_info=True)
        return error(f'删除标签失败: {str(e)}', status_code=500)


@bp.route('/all', methods=['GET'])
def get_all_tags():
    """获取所有标签（不分页，用于下拉选择）"""
    try:
        tags = Tag.query.order_by(Tag.name).all()
        return success([tag.to_dict() for tag in tags])
    except Exception as e:
        logger.error(f"获取所有标签失败: {e}", exc_info=True)
        return error(f'获取所有标签失败: {str(e)}', status_code=500)


@bp.route('/batch', methods=['POST'])
def batch_get_or_create_tags():
    """批量获取或创建标签 - 供工作流使用

    请求体:
    {
        "tags": ["标签1", "标签2", "标签3"],
        "auto_create": true  // 是否自动创建不存在的标签
    }

    返回:
    {
        "existing": [已存在的标签],
        "created": [新创建的标签],
        "all": [所有标签（已存在+新创建）]
    }
    """
    try:
        data = request.get_json()
        tag_names = data.get('tags', [])
        auto_create = data.get('auto_create', True)

        if not tag_names:
            return error('标签列表不能为空', status_code=400)

        # 去重并清理标签名
        tag_names = list(set([name.strip() for name in tag_names if name.strip()]))

        existing_tags = []
        created_tags = []

        for name in tag_names:
            tag = Tag.query.filter_by(name=name).first()
            if tag:
                existing_tags.append(tag)
            elif auto_create:
                # 自动创建新标签
                new_tag = Tag(
                    name=name,
                    description=f'自动创建的标签',
                    color='#909399'  # 灰色表示自动创建
                )
                db.session.add(new_tag)
                db.session.flush()  # 获取ID
                created_tags.append(new_tag)

        db.session.commit()

        all_tags = existing_tags + created_tags

        return success({
            'existing': [tag.to_dict() for tag in existing_tags],
            'created': [tag.to_dict() for tag in created_tags],
            'all': [tag.to_dict() for tag in all_tags]
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"批量处理标签失败: {e}", exc_info=True)
        return error(f'批量处理标签失败: {str(e)}', status_code=500)


@bp.route('/match', methods=['POST'])
def match_tags():
    """智能匹配标签 - 根据文章内容或关键词匹配现有标签

    请求体:
    {
        "keywords": ["关键词1", "关键词2"],  // 从文章提取的关键词
        "content": "文章内容（可选）",
        "max_tags": 5  // 最多返回的标签数
    }
    """
    try:
        data = request.get_json()
        keywords = data.get('keywords', [])
        content = data.get('content', '')
        max_tags = data.get('max_tags', 5)

        if not keywords and not content:
            return error('请提供关键词或内容', status_code=400)

        # 获取所有标签
        all_tags = Tag.query.all()

        matched_tags = []

        # 关键词完全匹配
        for keyword in keywords:
            keyword_lower = keyword.lower().strip()
            for tag in all_tags:
                if tag.name.lower() == keyword_lower and tag not in matched_tags:
                    matched_tags.append(tag)

        # 关键词部分匹配
        for keyword in keywords:
            keyword_lower = keyword.lower().strip()
            for tag in all_tags:
                if tag not in matched_tags:
                    if keyword_lower in tag.name.lower() or tag.name.lower() in keyword_lower:
                        matched_tags.append(tag)

        # 内容匹配（如果提供了内容）
        if content and len(matched_tags) < max_tags:
            content_lower = content.lower()
            for tag in all_tags:
                if tag not in matched_tags:
                    if tag.name.lower() in content_lower:
                        matched_tags.append(tag)

        # 限制返回数量
        matched_tags = matched_tags[:max_tags]

        return success({
            'matched': [tag.to_dict() for tag in matched_tags],
            'count': len(matched_tags)
        })

    except Exception as e:
        logger.error(f"匹配标签失败: {e}", exc_info=True)
        return error(f'匹配标签失败: {str(e)}', status_code=500)


@bp.route('/by-names', methods=['POST'])
def get_tags_by_names():
    """根据标签名称列表获取标签

    请求体:
    {
        "names": ["标签1", "标签2"]
    }
    """
    try:
        data = request.get_json()
        names = data.get('names', [])

        if not names:
            return success([])

        tags = Tag.query.filter(Tag.name.in_(names)).all()

        return success({
            'tags': [tag.to_dict() for tag in tags],
            'found': [tag.name for tag in tags],
            'not_found': [name for name in names if name not in [t.name for t in tags]]
        })

    except Exception as e:
        logger.error(f"根据名称获取标签失败: {e}", exc_info=True)
        return error(f'根据名称获取标签失败: {str(e)}', status_code=500)

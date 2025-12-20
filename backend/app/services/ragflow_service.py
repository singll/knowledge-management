"""RagFlow 服务封装"""
import logging
import tempfile
from pathlib import Path
from datetime import datetime
import requests
from flask import current_app

logger = logging.getLogger(__name__)

class RagFlowService:
    """RagFlow API 服务"""
    
    def __init__(self):
        self.base_url = current_app.config['RAGFLOW_URL'].rstrip('/')
        self.api_key = current_app.config['RAGFLOW_API_KEY']
        self.timeout = 30
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        })
        logger.info(f"RagFlow 服务初始化: {self.base_url}")
    
    # ========== Dataset (知识库) 管理 ==========
    
    def list_datasets(self, page=1, page_size=30, orderby='create_time', desc=True, name=None):
        """列出知识库"""
        url = f"{self.base_url}/api/v1/datasets"
        params = {
            'page': page,
            'page_size': page_size,
            'orderby': orderby,
            'desc': desc
        }
        if name:
            params['name'] = name
        
        logger.info(f"获取知识库列表: page={page}, size={page_size}")
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def get_dataset(self, dataset_id):
        """获取知识库详情"""
        url = f"{self.base_url}/api/v1/datasets/{dataset_id}"
        logger.info(f"获取知识库详情: {dataset_id}")
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def create_dataset(self, name, avatar='', description='', language='English', 
                      embedding_model='BAAI/bge-large-zh-v1.5', permission='me',
                      chunk_method='naive', parser_config=None):
        """创建知识库"""
        url = f"{self.base_url}/api/v1/datasets"
        data = {
            'name': name,
            'avatar': avatar,
            'description': description,
            'language': language,
            'embedding_model': embedding_model,
            'permission': permission,
            'chunk_method': chunk_method
        }
        if parser_config:
            data['parser_config'] = parser_config
        
        logger.info(f"创建知识库: {name}")
        response = self.session.post(url, json=data, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def update_dataset(self, dataset_id, name=None, description=None, 
                      embedding_model=None, chunk_method=None, parser_config=None):
        """更新知识库"""
        url = f"{self.base_url}/api/v1/datasets/{dataset_id}"
        data = {}
        if name:
            data['name'] = name
        if description is not None:
            data['description'] = description
        if embedding_model:
            data['embedding_model'] = embedding_model
        if chunk_method:
            data['chunk_method'] = chunk_method
        if parser_config:
            data['parser_config'] = parser_config
        
        logger.info(f"更新知识库: {dataset_id}")
        response = self.session.put(url, json=data, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def delete_dataset(self, dataset_id):
        """删除知识库"""
        url = f"{self.base_url}/api/v1/datasets/{dataset_id}"
        logger.info(f"删除知识库: {dataset_id}")
        response = self.session.delete(url, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    # ========== Document (文档) 管理 ==========
    
    def upload_string(self, dataset_id, content, filename='document.md', 
                     parser_id='naive', run='1', wait=False):
        """上传字符串内容到 RagFlow"""
        temp_file = self._create_temp_file(content, filename)
        try:
            result = self._upload_file(dataset_id, temp_file, filename, parser_id, run)
            document_id = result.get('document_id')
            
            if wait and run == '1' and document_id:
                status = self._wait_for_parsing(dataset_id, document_id)
                result['status'] = status
            
            return result
        finally:
            self._cleanup_temp_file(temp_file)
    
    def _create_temp_file(self, content, filename):
        """创建临时文件"""
        suffix = Path(filename).suffix or '.txt'
        temp_file = Path(current_app.config['TEMP_DIR']) / \
                   f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
        temp_file.write_text(content, encoding='utf-8')
        return temp_file
    
    def _cleanup_temp_file(self, file_path):
        """清理临时文件"""
        try:
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            logger.warning(f"清理临时文件失败: {e}")
    
    def _upload_file(self, dataset_id, file_path, filename, parser_id, run):
        """上传文件到 RagFlow"""
        url = f"{self.base_url}/api/v1/datasets/{dataset_id}/documents"
        data = {'name': filename, 'parser_id': parser_id, 'run': run}
        
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f, 'application/octet-stream')}
            response = self.session.post(url, data=data, files=files, timeout=self.timeout)
        
        response.raise_for_status()
        result = response.json()
        
        if result.get('code') != 0:
            raise Exception(f"上传失败: {result.get('message')}")
        
        data_field = result.get('data', {})
        document_id = None
        if isinstance(data_field, list) and len(data_field) > 0:
            document_id = data_field[0].get('id')
        elif isinstance(data_field, dict):
            document_id = data_field.get('id')
        
        return {'document_id': document_id, 'raw_response': result}
    
    def list_documents(self, dataset_id, page=1, page_size=20, keywords=None):
        """列出文档"""
        url = f"{self.base_url}/api/v1/datasets/{dataset_id}/documents"
        params = {'page': page, 'page_size': page_size}
        if keywords:
            params['keywords'] = keywords
        
        logger.info(f"获取文档列表: dataset={dataset_id}, page={page}")
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def get_document(self, dataset_id, document_id):
        """获取文档详情"""
        url = f"{self.base_url}/api/v1/datasets/{dataset_id}/documents/{document_id}"
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def delete_document(self, dataset_id, document_id):
        """删除文档"""
        url = f"{self.base_url}/api/v1/datasets/{dataset_id}/documents/{document_id}"
        response = self.session.delete(url, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def download_document(self, dataset_id, document_id):
        """下载文档"""
        url = f"{self.base_url}/api/v1/datasets/{dataset_id}/documents/{document_id}/download"
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.content
    
    def _wait_for_parsing(self, dataset_id, document_id, timeout=300):
        """等待解析完成"""
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self._get_parsing_status(dataset_id, document_id)
            if status.get('status') == 1:
                return 'completed'
            elif status.get('status') == 2:
                return 'failed'
            time.sleep(2)
        
        return 'timeout'
    
    def _get_parsing_status(self, dataset_id, document_id):
        """获取解析状态"""
        url = f"{self.base_url}/api/v1/datasets/{dataset_id}/documents/{document_id}/status"
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        result = response.json()
        return result.get('data', {})

    # ========== 文档解析 API ==========

    def run_parsing(self, dataset_id, document_ids):
        """触发文档解析

        Args:
            dataset_id: 知识库ID
            document_ids: 文档ID列表
        """
        url = f"{self.base_url}/api/v1/datasets/{dataset_id}/documents/run"
        data = {'document_ids': document_ids}

        logger.info(f"触发文档解析: dataset={dataset_id}, docs={document_ids}")
        response = self.session.post(url, json=data, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def stop_parsing(self, dataset_id, document_ids):
        """停止文档解析

        Args:
            dataset_id: 知识库ID
            document_ids: 文档ID列表
        """
        url = f"{self.base_url}/api/v1/datasets/{dataset_id}/documents/stop"
        data = {'document_ids': document_ids}

        logger.info(f"停止文档解析: dataset={dataset_id}, docs={document_ids}")
        response = self.session.post(url, json=data, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def get_parsing_status(self, dataset_id, document_id):
        """获取文档解析状态（公开方法）"""
        return self._get_parsing_status(dataset_id, document_id)

    # ========== 批量操作 API ==========

    def delete_documents_batch(self, dataset_id, document_ids):
        """批量删除文档

        Args:
            dataset_id: 知识库ID
            document_ids: 文档ID列表
        """
        url = f"{self.base_url}/api/v1/datasets/{dataset_id}/documents"
        # RagFlow 使用 DELETE 请求，document_ids 作为查询参数或请求体
        data = {'ids': document_ids}

        logger.info(f"批量删除文档: dataset={dataset_id}, count={len(document_ids)}")
        response = self.session.delete(url, json=data, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def transfer_document(self, source_dataset_id, target_dataset_id, document_id,
                         delete_source=True, parser_id='naive', run='1'):
        """将文档从一个知识库转移到另一个知识库

        Args:
            source_dataset_id: 源知识库ID
            target_dataset_id: 目标知识库ID
            document_id: 文档ID
            delete_source: 是否删除源文档
            parser_id: 解析器ID
            run: 是否立即解析 ('1' 或 '0')

        Returns:
            dict: 包含新文档ID的结果
        """
        # 1. 下载源文档
        logger.info(f"转移文档: {document_id} 从 {source_dataset_id} 到 {target_dataset_id}")

        content = self.download_document(source_dataset_id, document_id)

        # 2. 获取源文档信息
        doc_info = self.get_document(source_dataset_id, document_id)
        doc_data = doc_info.get('data', {})
        filename = doc_data.get('name', 'document.md')

        # 3. 上传到目标知识库
        temp_file = self._create_temp_file(
            content.decode('utf-8') if isinstance(content, bytes) else content,
            filename
        )
        try:
            result = self._upload_file(target_dataset_id, temp_file, filename, parser_id, run)
            new_document_id = result.get('document_id')

            # 4. 删除源文档（如果需要）
            if delete_source and new_document_id:
                self.delete_document(source_dataset_id, document_id)

            return {
                'success': True,
                'source_document_id': document_id,
                'target_document_id': new_document_id,
                'target_dataset_id': target_dataset_id,
                'filename': filename
            }
        finally:
            self._cleanup_temp_file(temp_file)

    def transfer_documents_batch(self, source_dataset_id, target_dataset_id,
                                 document_ids, delete_source=True, parser_id='naive', run='1'):
        """批量转移文档

        Args:
            source_dataset_id: 源知识库ID
            target_dataset_id: 目标知识库ID
            document_ids: 文档ID列表
            delete_source: 是否删除源文档
            parser_id: 解析器ID
            run: 是否立即解析

        Returns:
            dict: 转移结果统计
        """
        results = []
        success_count = 0
        fail_count = 0

        for doc_id in document_ids:
            try:
                result = self.transfer_document(
                    source_dataset_id, target_dataset_id, doc_id,
                    delete_source=delete_source, parser_id=parser_id, run=run
                )
                results.append(result)
                success_count += 1
            except Exception as e:
                logger.error(f"转移文档失败 {doc_id}: {e}")
                results.append({
                    'success': False,
                    'source_document_id': doc_id,
                    'error': str(e)
                })
                fail_count += 1

        return {
            'total': len(document_ids),
            'success': success_count,
            'failed': fail_count,
            'results': results
        }

    # ========== Chunk (分块) 管理 API ==========

    def list_chunks(self, dataset_id, document_id, page=1, page_size=20, keywords=None):
        """列出文档的分块"""
        url = f"{self.base_url}/api/v1/datasets/{dataset_id}/documents/{document_id}/chunks"
        params = {'page': page, 'page_size': page_size}
        if keywords:
            params['keywords'] = keywords

        logger.info(f"获取分块列表: dataset={dataset_id}, doc={document_id}")
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def delete_chunks(self, dataset_id, document_id, chunk_ids):
        """删除指定分块"""
        url = f"{self.base_url}/api/v1/datasets/{dataset_id}/documents/{document_id}/chunks"
        data = {'chunk_ids': chunk_ids}

        logger.info(f"删除分块: doc={document_id}, chunks={chunk_ids}")
        response = self.session.delete(url, json=data, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    # ========== Document Metadata (元数据) 管理 API ==========

    def update_document_metadata(self, dataset_id, document_id, meta_fields):
        """更新文档元数据

        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            meta_fields: 元数据字典，如 {"source_url": "https://...", "author": "xxx"}

        Returns:
            dict: API响应
        """
        url = f"{self.base_url}/api/v1/datasets/{dataset_id}/documents/{document_id}"
        data = {'meta_fields': meta_fields}

        logger.info(f"更新文档元数据: doc={document_id}, meta_fields={list(meta_fields.keys())}")
        response = self.session.put(url, json=data, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def search_documents_by_metadata(self, dataset_id, metadata_key, metadata_value):
        """根据元数据搜索文档

        由于 RagFlow 不直接支持按元数据搜索文档列表，
        我们需要遍历文档并检查 meta_fields

        Args:
            dataset_id: 知识库ID
            metadata_key: 元数据键名
            metadata_value: 元数据值

        Returns:
            list: 匹配的文档列表
        """
        # 获取所有文档（可能需要分页）
        page = 1
        page_size = 100
        matched_docs = []

        while True:
            result = self.list_documents(dataset_id, page=page, page_size=page_size)
            docs = result.get('data', {}).get('docs', [])

            if not docs:
                break

            for doc in docs:
                meta_fields = doc.get('meta_fields') or {}
                if meta_fields.get(metadata_key) == metadata_value:
                    matched_docs.append(doc)

            # 检查是否还有更多页
            total = result.get('data', {}).get('total', 0)
            if page * page_size >= total:
                break
            page += 1

        return matched_docs

    def check_url_in_ragflow(self, url, dataset_ids=None):
        """检查 URL 是否已存在于 RagFlow 中

        通过搜索文档元数据中的 source_url 字段来检查

        Args:
            url: 要检查的 URL
            dataset_ids: 可选，指定要搜索的知识库ID列表，默认搜索所有

        Returns:
            dict: {'exists': bool, 'document_id': str, 'dataset_id': str, ...}
        """
        from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

        # 规范化 URL
        def normalize_url(u):
            if not u:
                return u
            u = u.strip()
            parsed = urlparse(u)
            netloc = parsed.netloc.lower()
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

            return urlunparse((parsed.scheme, netloc, path, parsed.params, query, ''))

        normalized_url = normalize_url(url)

        # 获取要搜索的知识库列表
        if dataset_ids is None:
            datasets_result = self.list_datasets(page=1, page_size=100)
            datasets = datasets_result.get('data', [])
            dataset_ids = [ds.get('id') for ds in datasets if ds.get('id')]

        # 在每个知识库中搜索
        for dataset_id in dataset_ids:
            try:
                # 获取该知识库的所有文档
                page = 1
                while True:
                    result = self.list_documents(dataset_id, page=page, page_size=100)
                    docs = result.get('data', {}).get('docs', [])

                    if not docs:
                        break

                    for doc in docs:
                        meta_fields = doc.get('meta_fields') or {}
                        doc_url = meta_fields.get('source_url', '')

                        # 精确匹配
                        if doc_url == url:
                            return {
                                'exists': True,
                                'document_id': doc.get('id'),
                                'dataset_id': dataset_id,
                                'title': doc.get('name'),
                                'stored_url': doc_url,
                                'match_type': 'exact'
                            }

                        # 规范化匹配
                        if doc_url and normalize_url(doc_url) == normalized_url:
                            return {
                                'exists': True,
                                'document_id': doc.get('id'),
                                'dataset_id': dataset_id,
                                'title': doc.get('name'),
                                'stored_url': doc_url,
                                'match_type': 'normalized'
                            }

                    # 检查是否还有更多页
                    total = result.get('data', {}).get('total', 0)
                    if page * 100 >= total:
                        break
                    page += 1

            except Exception as e:
                logger.warning(f"搜索知识库 {dataset_id} 时出错: {e}")
                continue

        return {'exists': False}

    def batch_check_urls_in_ragflow(self, urls, dataset_ids=None):
        """批量检查 URL 是否已存在于 RagFlow 中

        Args:
            urls: URL 列表
            dataset_ids: 可选，指定要搜索的知识库ID列表

        Returns:
            dict: {url: {'exists': bool, ...}, ...}
        """
        from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

        def normalize_url(u):
            if not u:
                return u
            u = u.strip()
            parsed = urlparse(u)
            netloc = parsed.netloc.lower()
            path = parsed.path.rstrip('/')
            tracking_params = {'utm_source', 'utm_medium', 'utm_campaign', 'utm_term',
                              'utm_content', 'fbclid', 'gclid', 'ref', 'source'}
            if parsed.query:
                params = parse_qs(parsed.query)
                filtered_params = {k: v for k, v in params.items() if k.lower() not in tracking_params}
                query = urlencode(filtered_params, doseq=True) if filtered_params else ''
            else:
                query = ''
            return urlunparse((parsed.scheme, netloc, path, parsed.params, query, ''))

        # 构建 URL 查找映射
        url_set = set(urls)
        normalized_map = {normalize_url(u): u for u in urls}
        results = {u: {'exists': False} for u in urls}

        # 获取要搜索的知识库列表
        if dataset_ids is None:
            datasets_result = self.list_datasets(page=1, page_size=100)
            datasets = datasets_result.get('data', [])
            dataset_ids = [ds.get('id') for ds in datasets if ds.get('id')]

        # 在每个知识库中搜索
        for dataset_id in dataset_ids:
            try:
                page = 1
                while True:
                    result = self.list_documents(dataset_id, page=page, page_size=100)
                    docs = result.get('data', {}).get('docs', [])

                    if not docs:
                        break

                    for doc in docs:
                        meta_fields = doc.get('meta_fields') or {}
                        doc_url = meta_fields.get('source_url', '')

                        if not doc_url:
                            continue

                        # 精确匹配
                        if doc_url in url_set:
                            results[doc_url] = {
                                'exists': True,
                                'document_id': doc.get('id'),
                                'dataset_id': dataset_id,
                                'match_type': 'exact'
                            }

                        # 规范化匹配
                        normalized_doc_url = normalize_url(doc_url)
                        if normalized_doc_url in normalized_map:
                            original_url = normalized_map[normalized_doc_url]
                            if not results[original_url].get('exists'):
                                results[original_url] = {
                                    'exists': True,
                                    'document_id': doc.get('id'),
                                    'dataset_id': dataset_id,
                                    'match_type': 'normalized'
                                }

                    total = result.get('data', {}).get('total', 0)
                    if page * 100 >= total:
                        break
                    page += 1

            except Exception as e:
                logger.warning(f"搜索知识库 {dataset_id} 时出错: {e}")
                continue

        return results

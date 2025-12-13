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

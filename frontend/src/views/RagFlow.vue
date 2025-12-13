<template>
  <div class="ragflow-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>RagFlow 文档管理</span>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <!-- 上传文档 -->
        <el-tab-pane label="上传文档" name="upload">
          <el-form :model="uploadForm" :rules="uploadRules" ref="uploadFormRef" label-width="120px">
            <el-form-item label="Dataset ID" prop="dataset_id">
              <el-input v-model="uploadForm.dataset_id" placeholder="请输入 Dataset ID" />
            </el-form-item>
            <el-form-item label="文件名" prop="filename">
              <el-input v-model="uploadForm.filename" placeholder="例如: document.md" />
            </el-form-item>
            <el-form-item label="文档内容" prop="content">
              <el-input
                v-model="uploadForm.content"
                type="textarea"
                :rows="10"
                placeholder="请输入文档内容（支持 Markdown）"
              />
            </el-form-item>
            <el-form-item label="解析器">
              <el-select v-model="uploadForm.parser_id" placeholder="选择解析器">
                <el-option label="Naive" value="naive" />
                <el-option label="General" value="general" />
                <el-option label="Paper" value="paper" />
                <el-option label="Book" value="book" />
              </el-select>
            </el-form-item>
            <el-form-item label="自动解析">
              <el-switch v-model="uploadForm.auto_parse" />
            </el-form-item>
            <el-form-item label="等待完成">
              <el-switch v-model="uploadForm.wait_for_completion" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleUpload" :loading="uploading">
                <el-icon><Upload /></el-icon>
                上传文档
              </el-button>
              <el-button @click="resetUploadForm">重置</el-button>
            </el-form-item>
          </el-form>

          <!-- 上传结果 -->
          <el-alert
            v-if="uploadResult"
            :title="uploadResult.success ? '上传成功' : '上传失败'"
            :type="uploadResult.success ? 'success' : 'error'"
            :description="uploadResult.message"
            show-icon
            :closable="false"
            style="margin-top: 20px;"
          />
        </el-tab-pane>

        <!-- 文档列表 -->
        <el-tab-pane label="文档列表" name="list">
          <el-form :inline="true" class="search-form">
            <el-form-item label="Dataset ID">
              <el-input v-model="listForm.dataset_id" placeholder="请输入 Dataset ID" />
            </el-form-item>
            <el-form-item label="关键词">
              <el-input v-model="listForm.keywords" placeholder="搜索关键词" clearable />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadDocuments">
                <el-icon><Search /></el-icon>
                查询
              </el-button>
            </el-form-item>
          </el-form>

          <el-table :data="documents" v-loading="loadingDocs" stripe>
            <el-table-column prop="id" label="Document ID" width="200" />
            <el-table-column prop="name" label="文件名" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="chunk_count" label="分块数" width="100" />
            <el-table-column prop="created_at" label="创建时间" width="180" />
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button link type="primary" @click="handleViewDetail(row)">详情</el-button>
                <el-button link type="danger" @click="handleDeleteDoc(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-model:current-page="listForm.page"
            v-model:page-size="listForm.page_size"
            :total="docTotal"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            @size-change="loadDocuments"
            @current-change="loadDocuments"
            style="margin-top: 20px; justify-content: center;"
          />
        </el-tab-pane>

        <!-- 批量上传 -->
        <el-tab-pane label="批量上传" name="batch">
          <el-form :model="batchForm" label-width="120px">
            <el-form-item label="Dataset ID" required>
              <el-input v-model="batchForm.dataset_id" placeholder="请输入 Dataset ID" />
            </el-form-item>
            <el-form-item label="文档列表">
              <el-button @click="handleAddBatchItem" :icon="Plus">添加文档</el-button>
            </el-form-item>
          </el-form>

          <div v-for="(item, index) in batchForm.documents" :key="index" class="batch-item">
            <el-card>
              <template #header>
                <div class="batch-item-header">
                  <span>文档 {{ index + 1 }}</span>
                  <el-button link type="danger" @click="handleRemoveBatchItem(index)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </template>
              <el-form label-width="100px">
                <el-form-item label="文件名">
                  <el-input v-model="item.filename" placeholder="例如: doc1.md" />
                </el-form-item>
                <el-form-item label="内容">
                  <el-input v-model="item.content" type="textarea" :rows="5" />
                </el-form-item>
              </el-form>
            </el-card>
          </div>

          <el-button
            type="primary"
            @click="handleBatchUpload"
            :loading="batchUploading"
            :disabled="!batchForm.dataset_id || batchForm.documents.length === 0"
            style="margin-top: 20px;"
          >
            <el-icon><Upload /></el-icon>
            批量上传
          </el-button>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { uploadString, listDocuments, deleteDocument, uploadBatch } from '@/api/ragflow'
import { Plus, Delete } from '@element-plus/icons-vue'

const activeTab = ref('upload')
const uploading = ref(false)
const uploadFormRef = ref(null)
const uploadResult = ref(null)
const loadingDocs = ref(false)
const documents = ref([])
const docTotal = ref(0)
const batchUploading = ref(false)

const uploadForm = reactive({
  dataset_id: '',
  filename: 'document.md',
  content: '',
  parser_id: 'naive',
  auto_parse: true,
  wait_for_completion: false
})

const uploadRules = {
  dataset_id: [{ required: true, message: '请输入 Dataset ID', trigger: 'blur' }],
  filename: [{ required: true, message: '请输入文件名', trigger: 'blur' }],
  content: [{ required: true, message: '请输入文档内容', trigger: 'blur' }]
}

const listForm = reactive({
  dataset_id: '',
  keywords: '',
  page: 1,
  page_size: 20
})

const batchForm = reactive({
  dataset_id: '',
  documents: []
})

const handleUpload = async () => {
  try {
    await uploadFormRef.value.validate()
    uploading.value = true
    uploadResult.value = null

    const res = await uploadString({
      dataset_id: uploadForm.dataset_id,
      content: uploadForm.content,
      filename: uploadForm.filename,
      parser_id: uploadForm.parser_id,
      run: uploadForm.auto_parse ? '1' : '0',
      wait_for_completion: uploadForm.wait_for_completion
    })

    uploadResult.value = {
      success: true,
      message: `文档 ID: ${res.data.document_id}`
    }
    ElMessage.success('上传成功')
  } catch (error) {
    uploadResult.value = {
      success: false,
      message: error.message || '上传失败'
    }
  } finally {
    uploading.value = false
  }
}

const resetUploadForm = () => {
  uploadFormRef.value.resetFields()
  uploadResult.value = null
}

const loadDocuments = async () => {
  if (!listForm.dataset_id) {
    ElMessage.warning('请输入 Dataset ID')
    return
  }

  loadingDocs.value = true
  try {
    const res = await listDocuments({
      dataset_id: listForm.dataset_id,
      page: listForm.page,
      page_size: listForm.page_size,
      keywords: listForm.keywords
    })

    const data = res.data?.data || {}
    documents.value = data.docs || []
    docTotal.value = data.total || 0
  } catch (error) {
    console.error('加载文档列表失败:', error)
  } finally {
    loadingDocs.value = false
  }
}

const getStatusType = (status) => {
  const map = {
    0: 'info',
    1: 'success',
    2: 'danger',
    3: 'warning'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    0: '待处理',
    1: '已完成',
    2: '失败',
    3: '处理中'
  }
  return map[status] || '未知'
}

const handleViewDetail = (row) => {
  ElMessageBox.alert(JSON.stringify(row, null, 2), '文档详情', {
    confirmButtonText: '关闭'
  })
}

const handleDeleteDoc = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除文档"${row.name}"吗？`, '提示', {
      type: 'warning'
    })

    await deleteDocument({
      dataset_id: listForm.dataset_id,
      document_id: row.id
    })

    ElMessage.success('删除成功')
    loadDocuments()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

const handleAddBatchItem = () => {
  batchForm.documents.push({
    filename: `document_${batchForm.documents.length + 1}.md`,
    content: ''
  })
}

const handleRemoveBatchItem = (index) => {
  batchForm.documents.splice(index, 1)
}

const handleBatchUpload = async () => {
  if (!batchForm.dataset_id) {
    ElMessage.warning('请输入 Dataset ID')
    return
  }

  if (batchForm.documents.length === 0) {
    ElMessage.warning('请至少添加一个文档')
    return
  }

  batchUploading.value = true
  try {
    const res = await uploadBatch({
      dataset_id: batchForm.dataset_id,
      documents: batchForm.documents,
      parser_id: 'naive',
      run: '1'
    })

    const results = res.data.results || []
    const successCount = results.filter(r => r.success).length
    ElMessage.success(`批量上传完成，成功 ${successCount}/${results.length} 个`)

    // 重置表单
    batchForm.documents = []
  } catch (error) {
    console.error('批量上传失败:', error)
  } finally {
    batchUploading.value = false
  }
}
</script>

<style scoped>
.ragflow-container {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.batch-item {
  margin-bottom: 15px;
}

.batch-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

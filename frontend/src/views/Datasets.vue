<template>
  <div class="datasets-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>知识库管理</span>
          <div>
            <el-button type="primary" @click="handleRefresh">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button type="warning" @click="activeTab = 'upload'">
              <el-icon><Upload /></el-icon>
              上传文档
            </el-button>
            <el-button type="success" @click="handleCreateMapping">
              <el-icon><Plus /></el-icon>
              新建映射
            </el-button>
          </div>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <!-- RagFlow 知识库列表 -->
        <el-tab-pane label="知识库列表" name="ragflow">
          <el-table :data="ragflowDatasets" v-loading="loadingRagflow" stripe>
            <el-table-column prop="id" label="Dataset ID" width="280">
              <template #default="{ row }">
                <el-tooltip :content="row.id" placement="top">
                  <span class="dataset-id">{{ row.id }}</span>
                </el-tooltip>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="知识库名称" />
            <el-table-column prop="description" label="描述" show-overflow-tooltip />
            <el-table-column prop="document_count" label="文档数" width="100" />
            <el-table-column prop="chunk_count" label="分块数" width="100" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === '1' ? 'success' : 'info'" size="small">
                  {{ row.status === '1' ? '就绪' : '处理中' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="250">
              <template #default="{ row }">
                <el-button link type="primary" @click="handleViewDocuments(row)">
                  查看文档
                </el-button>
                <el-button link type="warning" @click="handleUploadToDataset(row)">
                  上传
                </el-button>
                <el-button link type="success" @click="handleQuickCreateMapping(row)">
                  创建映射
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 知识库映射管理 -->
        <el-tab-pane label="知识库映射" name="mapping">
          <el-table :data="mappings" v-loading="loadingMappings" stripe>
            <el-table-column prop="name" label="映射名称" width="150" />
            <el-table-column prop="display_name" label="显示名称" width="150" />
            <el-table-column prop="dataset_id" label="Dataset ID" width="280">
              <template #default="{ row }">
                <el-tooltip :content="row.dataset_id" placement="top">
                  <span class="dataset-id">{{ row.dataset_id }}</span>
                </el-tooltip>
              </template>
            </el-table-column>
            <el-table-column label="关联标签">
              <template #default="{ row }">
                <el-tag
                  v-for="tag in row.tags"
                  :key="tag.id"
                  :color="tag.color"
                  style="color: #fff; margin-right: 5px;"
                  size="small"
                >
                  {{ tag.name }}
                </el-tag>
                <span v-if="!row.tags || row.tags.length === 0" style="color: #999;">
                  未关联标签
                </span>
              </template>
            </el-table-column>
            <el-table-column label="默认" width="80">
              <template #default="{ row }">
                <el-tag v-if="row.is_default" type="success" size="small">默认</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                  {{ row.is_active ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button link type="primary" @click="handleEditMapping(row)">编辑</el-button>
                <el-button link type="danger" @click="handleDeleteMapping(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 文档列表 -->
        <el-tab-pane label="文档列表" name="documents" v-if="selectedDataset">
          <div class="document-header">
            <span>知识库: {{ selectedDataset.name }} ({{ selectedDataset.id }})</span>
            <el-button link type="primary" @click="selectedDataset = null; activeTab = 'ragflow'">
              返回
            </el-button>
          </div>

          <el-form :inline="true" class="search-form">
            <el-form-item label="关键词">
              <el-input v-model="docSearchKeyword" placeholder="搜索文档" clearable />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadDocuments">搜索</el-button>
            </el-form-item>
          </el-form>

          <el-table :data="documents" v-loading="loadingDocs" stripe>
            <el-table-column prop="name" label="文档名称" show-overflow-tooltip />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getDocStatusType(row.status)" size="small">
                  {{ getDocStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="chunk_count" label="分块数" width="100" />
            <el-table-column prop="size" label="大小" width="100">
              <template #default="{ row }">
                {{ formatSize(row.size) }}
              </template>
            </el-table-column>
            <el-table-column label="关联标签">
              <template #default="{ row }">
                <el-tag
                  v-for="tag in row.article_tags"
                  :key="tag.id"
                  :color="tag.color"
                  style="color: #fff; margin-right: 5px;"
                  size="small"
                >
                  {{ tag.name }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button link type="primary" @click="handleViewDocDetail(row)">详情</el-button>
                <el-button link type="danger" @click="handleDeleteDoc(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-model:current-page="docPagination.page"
            v-model:page-size="docPagination.page_size"
            :total="docPagination.total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            @size-change="loadDocuments"
            @current-change="loadDocuments"
            style="margin-top: 20px; justify-content: center;"
          />
        </el-tab-pane>

        <!-- 上传文档 -->
        <el-tab-pane label="上传文档" name="upload">
          <el-form :model="uploadForm" :rules="uploadRules" ref="uploadFormRef" label-width="120px">
            <el-form-item label="选择知识库" prop="dataset_id">
              <el-select
                v-model="uploadForm.dataset_id"
                placeholder="请选择知识库"
                filterable
                class="full-width"
              >
                <el-option
                  v-for="ds in ragflowDatasets"
                  :key="ds.id"
                  :label="ds.name"
                  :value="ds.id"
                />
              </el-select>
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
              <el-select v-model="uploadForm.parser_id" placeholder="选择解析器" class="full-width">
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

          <!-- 批量上传区域 -->
          <el-divider content-position="left">批量上传</el-divider>

          <el-form :model="batchForm" label-width="120px">
            <el-form-item label="选择知识库" required>
              <el-select
                v-model="batchForm.dataset_id"
                placeholder="请选择知识库"
                filterable
                class="full-width"
              >
                <el-option
                  v-for="ds in ragflowDatasets"
                  :key="ds.id"
                  :label="ds.name"
                  :value="ds.id"
                />
              </el-select>
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

    <!-- 创建/编辑映射对话框 -->
    <el-dialog
      v-model="mappingDialogVisible"
      :title="mappingForm.id ? '编辑知识库映射' : '新建知识库映射'"
      width="600px"
    >
      <el-form :model="mappingForm" :rules="mappingRules" ref="mappingFormRef" label-width="120px">
        <el-form-item label="映射名称" prop="name">
          <el-input v-model="mappingForm.name" placeholder="如: security, news, ai" />
          <div class="form-tip">用于工作流中识别知识库的唯一标识</div>
        </el-form-item>
        <el-form-item label="显示名称" prop="display_name">
          <el-input v-model="mappingForm.display_name" placeholder="如: 安全知识库" />
        </el-form-item>
        <el-form-item label="Dataset ID" prop="dataset_id">
          <el-select
            v-model="mappingForm.dataset_id"
            placeholder="选择知识库"
            filterable
            class="full-width"
          >
            <el-option
              v-for="ds in ragflowDatasets"
              :key="ds.id"
              :label="`${ds.name} (${ds.id})`"
              :value="ds.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="关联标签">
          <el-select
            v-model="mappingForm.tag_ids"
            multiple
            placeholder="选择关联的标签"
            class="full-width"
          >
            <el-option
              v-for="tag in allTags"
              :key="tag.id"
              :label="tag.name"
              :value="tag.id"
            >
              <el-tag :color="tag.color" style="color: #fff;" size="small">{{ tag.name }}</el-tag>
            </el-option>
          </el-select>
          <div class="form-tip">关联标签后，文章可根据标签自动选择入库的知识库</div>
        </el-form-item>
        <el-form-item label="默认解析器">
          <el-select v-model="mappingForm.parser_id" class="full-width">
            <el-option label="Naive" value="naive" />
            <el-option label="General" value="general" />
            <el-option label="Paper" value="paper" />
            <el-option label="Book" value="book" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="mappingForm.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="mappingForm.is_default" />
          <span style="margin-left: 10px; color: #999;">默认知识库用于无法匹配标签时的兜底</span>
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="mappingForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="mappingDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitMapping" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 文档详情对话框 -->
    <el-dialog v-model="docDetailVisible" title="文档详情" width="700px">
      <el-descriptions :column="2" border v-if="selectedDoc">
        <el-descriptions-item label="文档ID" :span="2">{{ selectedDoc.id }}</el-descriptions-item>
        <el-descriptions-item label="文件名" :span="2">{{ selectedDoc.name }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getDocStatusType(selectedDoc.status)">
            {{ getDocStatusText(selectedDoc.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="分块数">{{ selectedDoc.chunk_count || 0 }}</el-descriptions-item>
        <el-descriptions-item label="大小">{{ formatSize(selectedDoc.size) }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ selectedDoc.create_time }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listDatasets, listDocuments, deleteDocument, uploadString, uploadBatch } from '@/api/ragflow'
import { listMappings, createMapping, updateMapping, deleteMapping } from '@/api/dataset-mapping'
import { getAllTags } from '@/api/tags'
import { getArticleTags } from '@/api/dataset-mapping'
import { Plus, Delete } from '@element-plus/icons-vue'

const route = useRoute()
const activeTab = ref('ragflow')
const loadingRagflow = ref(false)
const loadingMappings = ref(false)
const loadingDocs = ref(false)
const submitting = ref(false)
const uploading = ref(false)
const batchUploading = ref(false)

const ragflowDatasets = ref([])
const mappings = ref([])
const allTags = ref([])
const documents = ref([])

const selectedDataset = ref(null)
const docSearchKeyword = ref('')
const docPagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 上传表单
const uploadFormRef = ref(null)
const uploadResult = ref(null)
const uploadForm = reactive({
  dataset_id: '',
  filename: 'document.md',
  content: '',
  parser_id: 'naive',
  auto_parse: true,
  wait_for_completion: false
})

const uploadRules = {
  dataset_id: [{ required: true, message: '请选择知识库', trigger: 'change' }],
  filename: [{ required: true, message: '请输入文件名', trigger: 'blur' }],
  content: [{ required: true, message: '请输入文档内容', trigger: 'blur' }]
}

// 批量上传表单
const batchForm = reactive({
  dataset_id: '',
  documents: []
})

const mappingDialogVisible = ref(false)
const mappingFormRef = ref(null)
const mappingForm = reactive({
  id: null,
  name: '',
  display_name: '',
  dataset_id: '',
  description: '',
  is_default: false,
  is_active: true,
  parser_id: 'naive',
  tag_ids: []
})

const mappingRules = {
  name: [{ required: true, message: '请输入映射名称', trigger: 'blur' }],
  dataset_id: [{ required: true, message: '请选择知识库', trigger: 'change' }]
}

const docDetailVisible = ref(false)
const selectedDoc = ref(null)

// 加载 RagFlow 知识库列表
const loadRagflowDatasets = async () => {
  loadingRagflow.value = true
  try {
    const res = await listDatasets({ page: 1, page_size: 100 })
    ragflowDatasets.value = res.data?.data || []
  } catch (error) {
    console.error('加载 RagFlow 知识库失败:', error)
    ElMessage.error('加载 RagFlow 知识库失败')
  } finally {
    loadingRagflow.value = false
  }
}

// 加载知识库映射列表
const loadMappings = async () => {
  loadingMappings.value = true
  try {
    const res = await listMappings({ page: 1, per_page: 100 })
    mappings.value = res.data.items || []
  } catch (error) {
    console.error('加载知识库映射失败:', error)
  } finally {
    loadingMappings.value = false
  }
}

// 加载所有标签
const loadAllTags = async () => {
  try {
    const res = await getAllTags()
    allTags.value = res.data || []
  } catch (error) {
    console.error('加载标签失败:', error)
  }
}

// 加载文档列表
const loadDocuments = async () => {
  if (!selectedDataset.value) return

  loadingDocs.value = true
  try {
    const res = await listDocuments({
      dataset_id: selectedDataset.value.id,
      page: docPagination.page,
      page_size: docPagination.page_size,
      keywords: docSearchKeyword.value
    })

    const data = res.data?.data || {}
    documents.value = data.docs || []
    docPagination.total = data.total || 0

    // 加载每个文档的标签
    for (const doc of documents.value) {
      try {
        const tagRes = await getArticleTags(doc.id, { dataset_id: selectedDataset.value.id })
        doc.article_tags = (tagRes.data?.tags || []).map(at => at.tag)
      } catch (e) {
        doc.article_tags = []
      }
    }
  } catch (error) {
    console.error('加载文档列表失败:', error)
  } finally {
    loadingDocs.value = false
  }
}

// 刷新
const handleRefresh = () => {
  loadRagflowDatasets()
  loadMappings()
  loadAllTags()
}

// 查看文档
const handleViewDocuments = (dataset) => {
  selectedDataset.value = dataset
  activeTab.value = 'documents'
  loadDocuments()
}

// 快速创建映射
const handleQuickCreateMapping = (dataset) => {
  Object.assign(mappingForm, {
    id: null,
    name: '',
    display_name: dataset.name,
    dataset_id: dataset.id,
    description: dataset.description || '',
    is_default: false,
    is_active: true,
    parser_id: 'naive',
    tag_ids: []
  })
  mappingDialogVisible.value = true
}

// 创建映射
const handleCreateMapping = () => {
  Object.assign(mappingForm, {
    id: null,
    name: '',
    display_name: '',
    dataset_id: '',
    description: '',
    is_default: false,
    is_active: true,
    parser_id: 'naive',
    tag_ids: []
  })
  mappingDialogVisible.value = true
}

// 编辑映射
const handleEditMapping = (row) => {
  Object.assign(mappingForm, {
    id: row.id,
    name: row.name,
    display_name: row.display_name,
    dataset_id: row.dataset_id,
    description: row.description,
    is_default: row.is_default,
    is_active: row.is_active,
    parser_id: row.parser_id,
    tag_ids: (row.tags || []).map(t => t.id)
  })
  mappingDialogVisible.value = true
}

// 提交映射
const handleSubmitMapping = async () => {
  try {
    await mappingFormRef.value.validate()
    submitting.value = true

    const data = { ...mappingForm }

    if (mappingForm.id) {
      await updateMapping(mappingForm.id, data)
      ElMessage.success('更新成功')
    } else {
      await createMapping(data)
      ElMessage.success('创建成功')
    }

    mappingDialogVisible.value = false
    loadMappings()
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitting.value = false
  }
}

// 删除映射
const handleDeleteMapping = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除映射"${row.name}"吗？`, '提示', { type: 'warning' })
    await deleteMapping(row.id)
    ElMessage.success('删除成功')
    loadMappings()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

// 查看文档详情
const handleViewDocDetail = (doc) => {
  selectedDoc.value = doc
  docDetailVisible.value = true
}

// 删除文档
const handleDeleteDoc = async (doc) => {
  try {
    await ElMessageBox.confirm(`确定删除文档"${doc.name}"吗？`, '提示', { type: 'warning' })
    await deleteDocument({
      dataset_id: selectedDataset.value.id,
      document_id: doc.id
    })
    ElMessage.success('删除成功')
    loadDocuments()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

// 文档状态
const getDocStatusType = (status) => {
  const map = { 0: 'info', 1: 'success', 2: 'danger', 3: 'warning' }
  return map[status] || 'info'
}

const getDocStatusText = (status) => {
  const map = { 0: '待处理', 1: '已完成', 2: '失败', 3: '处理中' }
  return map[status] || '未知'
}

// 格式化大小
const formatSize = (bytes) => {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

// 上传到指定知识库
const handleUploadToDataset = (dataset) => {
  uploadForm.dataset_id = dataset.id
  batchForm.dataset_id = dataset.id
  activeTab.value = 'upload'
}

// 上传单个文档
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

// 重置上传表单
const resetUploadForm = () => {
  uploadFormRef.value.resetFields()
  uploadResult.value = null
}

// 添加批量上传项
const handleAddBatchItem = () => {
  batchForm.documents.push({
    filename: `document_${batchForm.documents.length + 1}.md`,
    content: ''
  })
}

// 移除批量上传项
const handleRemoveBatchItem = (index) => {
  batchForm.documents.splice(index, 1)
}

// 批量上传
const handleBatchUpload = async () => {
  if (!batchForm.dataset_id) {
    ElMessage.warning('请选择知识库')
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

onMounted(() => {
  // 根据 URL 参数切换 tab
  const tab = route.query.tab
  if (tab === 'mapping') {
    activeTab.value = 'mapping'
  } else if (tab === 'upload') {
    activeTab.value = 'upload'
  }

  loadRagflowDatasets()
  loadMappings()
  loadAllTags()
})
</script>

<style scoped>
.datasets-container {
  max-width: 1600px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dataset-id {
  font-family: monospace;
  font-size: 12px;
  color: #666;
}

.document-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.search-form {
  margin-bottom: 20px;
}

.full-width {
  width: 100%;
}

.form-tip {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
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

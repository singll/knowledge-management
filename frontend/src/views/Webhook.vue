<template>
  <div class="webhook-container">
    <el-row :gutter="20">
      <!-- 左侧：触发器 -->
      <el-col :span="10">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon><Connection /></el-icon>
              <span>触发 Webhook</span>
            </div>
          </template>

          <el-form :model="triggerForm" :rules="triggerRules" ref="triggerFormRef" label-width="120px">
            <el-form-item label="选择 Webhook" prop="webhook_id">
              <el-select
                v-model="triggerForm.webhook_id"
                placeholder="选择 Webhook 配置"
                style="width: 100%;"
                @change="handleWebhookChange"
              >
                <el-option
                  v-for="wh in activeWebhooks"
                  :key="wh.id"
                  :label="wh.name"
                  :value="wh.id"
                >
                  <div style="display: flex; justify-content: space-between;">
                    <span>{{ wh.name }}</span>
                    <el-tag size="small" type="success">{{ wh.method }}</el-tag>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>

            <el-form-item label="Webhook URL" v-if="selectedWebhook">
              <el-input :value="selectedWebhook.url" readonly>
                <template #append>
                  <el-button :icon="CopyDocument" @click="copyUrl" />
                </template>
              </el-input>
            </el-form-item>

            <el-form-item label="文章链接" prop="article_url">
              <el-input
                v-model="triggerForm.article_url"
                placeholder="https://example.com/article"
                clearable
              />
            </el-form-item>

            <el-form-item label="额外数据">
              <el-input
                v-model="triggerForm.extra_data_json"
                type="textarea"
                :rows="4"
                placeholder='{"key": "value"}'
              />
              <div class="form-tip">可选，JSON 格式的额外数据</div>
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                @click="handleTrigger"
                :loading="triggering"
                :disabled="!triggerForm.webhook_id || !triggerForm.article_url"
              >
                <el-icon><Promotion /></el-icon>
                触发 Webhook
              </el-button>
              <el-button @click="resetTriggerForm">重置</el-button>
            </el-form-item>
          </el-form>

          <!-- 触发结果 -->
          <el-alert
            v-if="triggerResult"
            :title="triggerResult.success ? '触发成功' : '触发失败'"
            :type="triggerResult.success ? 'success' : 'error'"
            :description="triggerResult.message"
            show-icon
            :closable="false"
            style="margin-top: 20px;"
          />
        </el-card>
      </el-col>

      <!-- 右侧：历史记录 -->
      <el-col :span="14">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>调用历史</span>
              <el-button @click="loadHistory" :icon="Refresh">刷新</el-button>
            </div>
          </template>

          <el-form :inline="true" class="search-form">
            <el-form-item label="Webhook">
              <el-select v-model="historyFilter.webhook_id" placeholder="全部" clearable>
                <el-option
                  v-for="wh in allWebhooks"
                  :key="wh.id"
                  :label="wh.name"
                  :value="wh.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="historyFilter.status" placeholder="全部" clearable>
                <el-option label="等待中" value="pending" />
                <el-option label="成功" value="success" />
                <el-option label="失败" value="failed" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadHistory">查询</el-button>
            </el-form-item>
          </el-form>

          <el-table :data="historyData" v-loading="loadingHistory" stripe max-height="600">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="webhook_name" label="Webhook" width="120" />
            <el-table-column prop="article_url" label="文章链接" min-width="200">
              <template #default="{ row }">
                <el-link :href="row.article_url" target="_blank" type="primary" :underline="false">
                  {{ truncateUrl(row.article_url) }}
                </el-link>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="response_code" label="响应码" width="90" />
            <el-table-column prop="created_at" label="时间" width="160" />
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button link type="primary" @click="handleViewHistory(row)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-model:current-page="historyPagination.page"
            v-model:page-size="historyPagination.per_page"
            :total="historyPagination.total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            @size-change="loadHistory"
            @current-change="loadHistory"
            style="margin-top: 20px; justify-content: center;"
          />
        </el-card>
      </el-col>
    </el-row>

    <!-- Webhook 配置管理 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>Webhook 配置管理</span>
          <el-button type="primary" @click="handleCreateConfig">
            <el-icon><Plus /></el-icon>
            新建配置
          </el-button>
        </div>
      </template>

      <el-table :data="allWebhooks" v-loading="loadingConfigs" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="名称" width="150" />
        <el-table-column prop="url" label="URL" min-width="300" />
        <el-table-column prop="method" label="方法" width="80">
          <template #default="{ row }">
            <el-tag size="small">{{ row.method }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" width="200" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEditConfig(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDeleteConfig(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 配置对话框 -->
    <el-dialog
      v-model="configDialogVisible"
      :title="configDialogTitle"
      width="600px"
    >
      <el-form :model="configForm" :rules="configRules" ref="configFormRef" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="configForm.name" placeholder="例如：保存文章到知识库" />
        </el-form-item>
        <el-form-item label="Webhook URL" prop="url">
          <el-input v-model="configForm.url" placeholder="https://n8n.example.com/webhook/..." />
        </el-form-item>
        <el-form-item label="请求方法" prop="method">
          <el-select v-model="configForm.method">
            <el-option label="POST" value="POST" />
            <el-option label="GET" value="GET" />
            <el-option label="PUT" value="PUT" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="configForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="configForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="configDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitConfig" :loading="submittingConfig">确定</el-button>
      </template>
    </el-dialog>

    <!-- 历史详情对话框 -->
    <el-dialog v-model="historyDetailVisible" title="调用详情" width="700px">
      <el-descriptions :column="1" border v-if="currentHistory">
        <el-descriptions-item label="ID">{{ currentHistory.id }}</el-descriptions-item>
        <el-descriptions-item label="Webhook">{{ currentHistory.webhook_name }}</el-descriptions-item>
        <el-descriptions-item label="文章链接">
          <el-link :href="currentHistory.article_url" target="_blank" type="primary">
            {{ currentHistory.article_url }}
          </el-link>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentHistory.status)">
            {{ getStatusText(currentHistory.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="响应码">{{ currentHistory.response_code || '-' }}</el-descriptions-item>
        <el-descriptions-item label="时间">{{ currentHistory.created_at }}</el-descriptions-item>
        <el-descriptions-item label="请求数据">
          <el-input
            :value="currentHistory.payload"
            type="textarea"
            :rows="5"
            readonly
          />
        </el-descriptions-item>
        <el-descriptions-item label="响应数据">
          <el-input
            :value="currentHistory.response_body || '无'"
            type="textarea"
            :rows="5"
            readonly
          />
        </el-descriptions-item>
        <el-descriptions-item label="错误信息" v-if="currentHistory.error_message">
          <el-alert :title="currentHistory.error_message" type="error" :closable="false" />
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CopyDocument, Refresh, Promotion } from '@element-plus/icons-vue'
import {
  listWebhookConfigs,
  createWebhookConfig,
  updateWebhookConfig,
  deleteWebhookConfig,
  triggerWebhook,
  listWebhookHistory
} from '@/api/webhook'

const triggering = ref(false)
const loadingHistory = ref(false)
const loadingConfigs = ref(false)
const submittingConfig = ref(false)
const triggerFormRef = ref(null)
const configFormRef = ref(null)
const triggerResult = ref(null)
const allWebhooks = ref([])
const historyData = ref([])
const configDialogVisible = ref(false)
const configDialogTitle = ref('新建配置')
const historyDetailVisible = ref(false)
const currentHistory = ref(null)

const activeWebhooks = computed(() => allWebhooks.value.filter(w => w.is_active))
const selectedWebhook = computed(() => 
  allWebhooks.value.find(w => w.id === triggerForm.webhook_id)
)

const triggerForm = reactive({
  webhook_id: null,
  article_url: '',
  extra_data_json: ''
})

const triggerRules = {
  webhook_id: [{ required: true, message: '请选择 Webhook', trigger: 'change' }],
  article_url: [
    { required: true, message: '请输入文章链接', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL', trigger: 'blur' }
  ]
}

const historyFilter = reactive({
  webhook_id: null,
  status: ''
})

const historyPagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

const configForm = reactive({
  id: null,
  name: '',
  url: '',
  method: 'POST',
  description: '',
  is_active: true
})

const configRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  url: [
    { required: true, message: '请输入 Webhook URL', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL', trigger: 'blur' }
  ],
  method: [{ required: true, message: '请选择请求方法', trigger: 'change' }]
}

const loadConfigs = async () => {
  loadingConfigs.value = true
  try {
    const res = await listWebhookConfigs({ per_page: 100 })
    allWebhooks.value = res.data.items
  } catch (error) {
    console.error('加载配置失败:', error)
  } finally {
    loadingConfigs.value = false
  }
}

const loadHistory = async () => {
  loadingHistory.value = true
  try {
    const res = await listWebhookHistory({
      page: historyPagination.page,
      per_page: historyPagination.per_page,
      webhook_id: historyFilter.webhook_id,
      status: historyFilter.status
    })
    historyData.value = res.data.items
    historyPagination.total = res.data.pagination.total
  } catch (error) {
    console.error('加载历史失败:', error)
  } finally {
    loadingHistory.value = false
  }
}

const handleWebhookChange = () => {
  triggerResult.value = null
}

const handleTrigger = async () => {
  try {
    await triggerFormRef.value.validate()
    triggering.value = true
    triggerResult.value = null

    let extraData = null
    if (triggerForm.extra_data_json) {
      try {
        extraData = JSON.parse(triggerForm.extra_data_json)
      } catch (e) {
        ElMessage.error('额外数据不是有效的 JSON 格式')
        return
      }
    }

    const res = await triggerWebhook({
      webhook_id: triggerForm.webhook_id,
      article_url: triggerForm.article_url,
      extra_data: extraData
    })

    triggerResult.value = {
      success: true,
      message: `调用成功，历史记录 ID: ${res.data.id}`
    }
    ElMessage.success('Webhook 已触发')
    loadHistory()
  } catch (error) {
    triggerResult.value = {
      success: false,
      message: error.message || '触发失败'
    }
  } finally {
    triggering.value = false
  }
}

const resetTriggerForm = () => {
  triggerFormRef.value.resetFields()
  triggerResult.value = null
}

const copyUrl = () => {
  if (selectedWebhook.value) {
    navigator.clipboard.writeText(selectedWebhook.value.url)
    ElMessage.success('已复制到剪贴板')
  }
}

const handleCreateConfig = () => {
  configDialogTitle.value = '新建配置'
  Object.assign(configForm, {
    id: null,
    name: '',
    url: '',
    method: 'POST',
    description: '',
    is_active: true
  })
  configDialogVisible.value = true
}

const handleEditConfig = (row) => {
  configDialogTitle.value = '编辑配置'
  Object.assign(configForm, row)
  configDialogVisible.value = true
}

const handleSubmitConfig = async () => {
  try {
    await configFormRef.value.validate()
    submittingConfig.value = true

    if (configForm.id) {
      await updateWebhookConfig(configForm.id, configForm)
      ElMessage.success('更新成功')
    } else {
      await createWebhookConfig(configForm)
      ElMessage.success('创建成功')
    }

    configDialogVisible.value = false
    loadConfigs()
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submittingConfig.value = false
  }
}

const handleDeleteConfig = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除配置"${row.name}"吗？`, '提示', {
      type: 'warning'
    })
    await deleteWebhookConfig(row.id)
    ElMessage.success('删除成功')
    loadConfigs()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

const handleViewHistory = (row) => {
  currentHistory.value = row
  historyDetailVisible.value = true
}

const getStatusType = (status) => {
  const map = {
    pending: 'info',
    success: 'success',
    failed: 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    pending: '等待中',
    success: '成功',
    failed: '失败'
  }
  return map[status] || status
}

const truncateUrl = (url) => {
  return url.length > 50 ? url.substring(0, 50) + '...' : url
}

onMounted(() => {
  loadConfigs()
  loadHistory()
})
</script>

<style scoped>
.webhook-container {
  max-width: 1600px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.search-form {
  margin-bottom: 20px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>

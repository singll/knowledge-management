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
                class="full-width-select"
                @change="handleWebhookChange"
              >
                <el-option
                  v-for="wh in activeWebhooks"
                  :key="wh.id"
                  :label="wh.name"
                  :value="wh.id"
                >
                  <div class="select-option-content">
                    <span class="option-name">{{ wh.name }}</span>
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

            <!-- 动态变量输入区域 -->
            <template v-if="selectedWebhook && templateVariables.length > 0">
              <el-divider content-position="left">
                <el-icon><Edit /></el-icon>
                变量填写
              </el-divider>
              <el-form-item
                v-for="variable in templateVariables"
                :key="variable"
                :label="variable"
              >
                <el-input
                  v-model="variableValues[variable]"
                  :placeholder="`请输入 ${variable} 的值`"
                  clearable
                >
                  <template #prefix>
                    <el-icon><Key /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
              <el-divider />
            </template>

            <el-form-item label="请求体预览" v-if="selectedWebhook">
              <div class="json-editor-wrapper">
                <el-input
                  v-model="triggerForm.request_body"
                  type="textarea"
                  :rows="10"
                  placeholder='请输入 JSON 格式的请求体'
                  class="json-textarea"
                />
                <div class="json-editor-actions">
                  <el-button size="small" @click="formatJson">格式化 JSON</el-button>
                  <el-button size="small" @click="loadTemplateBody">加载模板</el-button>
                  <el-button size="small" type="primary" @click="applyVariables">应用变量</el-button>
                </div>
              </div>
              <div class="form-tip">
                <div>内置变量: <code v-pre>{{timestamp}}</code>, <code v-pre>{{date}}</code>, <code v-pre>{{webhook_name}}</code></div>
                <div v-if="templateVariables.length > 0" style="margin-top: 4px;">
                  自定义变量:
                  <code v-for="v in templateVariables" :key="v" style="margin-right: 8px;">{{ '{{' + v + '}}' }}</code>
                </div>
              </div>
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                @click="handleTrigger"
                :loading="triggering"
                :disabled="!triggerForm.webhook_id"
              >
                <el-icon><Promotion /></el-icon>
                发送请求
              </el-button>
              <el-button @click="resetTriggerForm">重置</el-button>
            </el-form-item>
          </el-form>

          <!-- 触发结果 -->
          <el-alert
            v-if="triggerResult"
            :title="triggerResult.success ? '请求成功' : '请求失败'"
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
              <el-select v-model="historyFilter.webhook_id" placeholder="全部" clearable class="filter-select">
                <el-option
                  v-for="wh in allWebhooks"
                  :key="wh.id"
                  :label="wh.name"
                  :value="wh.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="historyFilter.status" placeholder="全部" clearable class="filter-select">
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
            <el-table-column prop="request_url" label="请求URL" min-width="200">
              <template #default="{ row }">
                <el-tooltip :content="row.request_url || row.article_url" placement="top">
                  <span class="truncate-text">{{ truncateUrl(row.request_url || row.article_url) }}</span>
                </el-tooltip>
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
        <el-table-column prop="url" label="URL" min-width="300">
          <template #default="{ row }">
            <el-tooltip :content="row.url" placement="top">
              <span class="truncate-text">{{ row.url }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="method" label="方法" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="getMethodType(row.method)">{{ row.method }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="content_type" label="Content-Type" width="150">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ row.content_type || 'application/json' }}</el-tag>
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
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleTestConfig(row)">测试</el-button>
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
      width="800px"
      class="config-dialog"
    >
      <el-tabs v-model="configActiveTab">
        <el-tab-pane label="基本信息" name="basic">
          <el-form :model="configForm" :rules="configRules" ref="configFormRef" label-width="120px">
            <el-form-item label="名称" prop="name">
              <el-input v-model="configForm.name" placeholder="例如：保存文章到知识库" />
            </el-form-item>
            <el-form-item label="Webhook URL" prop="url">
              <el-input v-model="configForm.url" placeholder="http://n8n:5678/webhook/xxx 或 https://api.example.com/endpoint">
                <template #prepend>
                  <el-select v-model="configForm.method" style="width: 100px;">
                    <el-option label="GET" value="GET" />
                    <el-option label="POST" value="POST" />
                    <el-option label="PUT" value="PUT" />
                    <el-option label="PATCH" value="PATCH" />
                    <el-option label="DELETE" value="DELETE" />
                  </el-select>
                </template>
              </el-input>
              <div class="form-tip">支持内网地址如 http://n8n:5678/webhook/xxx</div>
            </el-form-item>
            <el-form-item label="Content-Type" prop="content_type">
              <el-select v-model="configForm.content_type" class="full-width-select">
                <el-option label="application/json" value="application/json" />
                <el-option label="application/x-www-form-urlencoded" value="application/x-www-form-urlencoded" />
                <el-option label="multipart/form-data" value="multipart/form-data" />
                <el-option label="text/plain" value="text/plain" />
              </el-select>
            </el-form-item>
            <el-form-item label="超时时间">
              <el-input-number v-model="configForm.timeout" :min="1" :max="300" />
              <span style="margin-left: 10px; color: #909399;">秒</span>
            </el-form-item>
            <el-form-item label="描述">
              <el-input v-model="configForm.description" type="textarea" :rows="2" />
            </el-form-item>
            <el-form-item label="启用">
              <el-switch v-model="configForm.is_active" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="请求头" name="headers">
          <div class="headers-editor">
            <div class="headers-tip">
              <el-alert type="info" :closable="false">
                配置自定义请求头，如 Authorization、X-API-Key 等
              </el-alert>
            </div>
            <div class="headers-list">
              <div v-for="(header, index) in configForm.headers" :key="index" class="header-item">
                <el-input v-model="header.key" placeholder="Header 名称" class="header-key" />
                <el-input v-model="header.value" placeholder="Header 值" class="header-value" />
                <el-button :icon="Delete" type="danger" circle @click="removeHeader(index)" />
              </div>
              <el-button type="primary" plain @click="addHeader">
                <el-icon><Plus /></el-icon>
                添加请求头
              </el-button>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="请求体模板" name="body">
          <div class="body-editor">
            <div class="body-tip">
              <el-alert type="info" :closable="false">
                <template #title>
                  配置默认请求体模板，支持以下变量:
                </template>
                <div class="variables-list">
                  <code v-pre>{{article_url}}</code> - 文章链接 &nbsp;
                  <code v-pre>{{timestamp}}</code> - 当前时间戳 &nbsp;
                  <code v-pre>{{webhook_name}}</code> - Webhook名称 &nbsp;
                  <code v-pre>{{date}}</code> - 当前日期
                </div>
              </el-alert>
            </div>
            <el-input
              v-model="configForm.body_template"
              type="textarea"
              :rows="12"
              placeholder='{
  "url": "{{article_url}}",
  "timestamp": "{{timestamp}}",
  "source": "knowledge-management"
}'
              class="json-textarea"
            />
            <div class="json-editor-actions">
              <el-button size="small" @click="formatConfigJson">格式化 JSON</el-button>
              <el-button size="small" @click="insertDefaultTemplate">插入默认模板</el-button>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
      <template #footer>
        <el-button @click="configDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitConfig" :loading="submittingConfig">确定</el-button>
      </template>
    </el-dialog>

    <!-- 历史详情对话框 -->
    <el-dialog v-model="historyDetailVisible" title="调用详情" width="900px" class="history-detail-dialog">
      <el-tabs v-model="historyDetailTab">
        <el-tab-pane label="概览" name="overview">
          <el-descriptions :column="2" border v-if="currentHistory">
            <el-descriptions-item label="ID">{{ currentHistory.id }}</el-descriptions-item>
            <el-descriptions-item label="Webhook">{{ currentHistory.webhook_name }}</el-descriptions-item>
            <el-descriptions-item label="请求方法">
              <el-tag size="small" :type="getMethodType(currentHistory.request_method || 'POST')">
                {{ currentHistory.request_method || 'POST' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusType(currentHistory.status)">
                {{ getStatusText(currentHistory.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="请求URL" :span="2">
              <div class="url-display">
                <span class="url-text">{{ currentHistory.request_url || currentHistory.article_url || '-' }}</span>
                <el-button
                  v-if="currentHistory.request_url || currentHistory.article_url"
                  link
                  type="primary"
                  :icon="CopyDocument"
                  @click="copyToClipboard(currentHistory.request_url || currentHistory.article_url)"
                />
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="响应码">
              <el-tag :type="getResponseCodeType(currentHistory.response_code)">
                {{ currentHistory.response_code || '-' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="耗时">
              <span :class="getDurationClass(currentHistory.duration)">
                {{ currentHistory.duration ? currentHistory.duration + ' ms' : '-' }}
              </span>
            </el-descriptions-item>
            <el-descriptions-item label="请求时间" :span="2">{{ currentHistory.created_at }}</el-descriptions-item>
            <el-descriptions-item label="错误信息" :span="2" v-if="currentHistory.error_message">
              <el-alert :title="currentHistory.error_message" type="error" :closable="false" />
            </el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>

        <el-tab-pane label="请求详情" name="request">
          <div class="detail-section">
            <div class="section-header">
              <h4>请求 URL</h4>
              <el-button size="small" :icon="CopyDocument" @click="copyToClipboard(currentHistory?.request_url || currentHistory?.article_url)">复制</el-button>
            </div>
            <div class="url-box">
              <el-tag :type="getMethodType(currentHistory?.request_method || 'POST')" class="method-tag">
                {{ currentHistory?.request_method || 'POST' }}
              </el-tag>
              <span class="url-content">{{ currentHistory?.request_url || currentHistory?.article_url || '-' }}</span>
            </div>
          </div>

          <div class="detail-section">
            <div class="section-header">
              <h4>请求头 (Request Headers)</h4>
              <el-button size="small" :icon="CopyDocument" @click="copyToClipboard(formatJsonDisplay(currentHistory?.request_headers))">复制</el-button>
            </div>
            <el-input
              :model-value="formatJsonDisplay(currentHistory?.request_headers) || '无'"
              type="textarea"
              :rows="6"
              readonly
              class="code-textarea"
            />
          </div>

          <div class="detail-section">
            <div class="section-header">
              <h4>请求体 (Request Body)</h4>
              <el-button size="small" :icon="CopyDocument" @click="copyToClipboard(formatJsonDisplay(currentHistory?.payload))">复制</el-button>
            </div>
            <el-input
              :model-value="formatJsonDisplay(currentHistory?.payload) || '无'"
              type="textarea"
              :rows="12"
              readonly
              class="code-textarea"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane label="响应详情" name="response">
          <div class="detail-section">
            <div class="section-header">
              <h4>响应状态</h4>
            </div>
            <div class="response-status">
              <el-tag :type="getResponseCodeType(currentHistory?.response_code)" size="large">
                {{ currentHistory?.response_code || '-' }}
              </el-tag>
              <span class="status-text">{{ getResponseCodeText(currentHistory?.response_code) }}</span>
              <span class="duration-text" v-if="currentHistory?.duration">
                耗时: {{ currentHistory.duration }} ms
              </span>
            </div>
          </div>

          <div class="detail-section">
            <div class="section-header">
              <h4>响应头 (Response Headers)</h4>
              <el-button size="small" :icon="CopyDocument" @click="copyToClipboard(formatJsonDisplay(currentHistory?.response_headers))">复制</el-button>
            </div>
            <el-input
              :model-value="formatJsonDisplay(currentHistory?.response_headers) || '无'"
              type="textarea"
              :rows="6"
              readonly
              class="code-textarea"
            />
          </div>

          <div class="detail-section">
            <div class="section-header">
              <h4>响应体 (Response Body)</h4>
              <el-button size="small" :icon="CopyDocument" @click="copyToClipboard(currentHistory?.response_body)">复制</el-button>
            </div>
            <el-input
              :model-value="formatResponseBody(currentHistory?.response_body) || '无'"
              type="textarea"
              :rows="12"
              readonly
              class="code-textarea"
            />
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CopyDocument, Refresh, Promotion, Delete, Edit, Key } from '@element-plus/icons-vue'
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
const configActiveTab = ref('basic')
const historyDetailTab = ref('overview')

// 变量值存储
const variableValues = reactive({})

const activeWebhooks = computed(() => allWebhooks.value.filter(w => w.is_active))
const selectedWebhook = computed(() =>
  allWebhooks.value.find(w => w.id === triggerForm.webhook_id)
)

// 从模板中提取自定义变量（排除内置变量）
const templateVariables = computed(() => {
  if (!selectedWebhook.value?.body_template) return []

  const template = selectedWebhook.value.body_template
  const variablePattern = /\{\{\s*(\w+)\s*\}\}/g
  const builtInVariables = ['timestamp', 'date', 'webhook_name']
  const variables = new Set()

  let match
  while ((match = variablePattern.exec(template)) !== null) {
    const varName = match[1]
    if (!builtInVariables.includes(varName)) {
      variables.add(varName)
    }
  }

  return Array.from(variables)
})

const triggerForm = reactive({
  webhook_id: null,
  request_body: ''
})

const triggerRules = {
  webhook_id: [{ required: true, message: '请选择 Webhook', trigger: 'change' }]
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
  content_type: 'application/json',
  timeout: 30,
  description: '',
  is_active: true,
  headers: [],
  body_template: ''
})

// 自定义URL验证器，支持内网地址
const validateUrl = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入 Webhook URL'))
    return
  }
  // 支持 http://hostname:port/path 格式，包括内网地址
  const urlPattern = /^https?:\/\/[a-zA-Z0-9][-a-zA-Z0-9]*(\.[a-zA-Z0-9][-a-zA-Z0-9]*)*(:\d+)?(\/.*)?$/
  if (urlPattern.test(value)) {
    callback()
  } else {
    callback(new Error('请输入有效的URL，支持 http://hostname:port/path 格式'))
  }
}

const configRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  url: [
    { required: true, message: '请输入 Webhook URL', trigger: 'blur' },
    { validator: validateUrl, trigger: 'blur' }
  ]
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

// 当选择webhook时，加载其body模板并重置变量
const handleWebhookChange = () => {
  triggerResult.value = null
  // 清空变量值
  Object.keys(variableValues).forEach(key => delete variableValues[key])

  if (selectedWebhook.value && selectedWebhook.value.body_template) {
    triggerForm.request_body = selectedWebhook.value.body_template
  } else {
    triggerForm.request_body = JSON.stringify({
      "url": "{{article_url}}",
      "timestamp": "{{timestamp}}",
      "source": "knowledge-management"
    }, null, 2)
  }
}

// 监听webhook变化自动加载模板
watch(() => triggerForm.webhook_id, () => {
  handleWebhookChange()
})

// 应用变量到请求体
const applyVariables = () => {
  if (!selectedWebhook.value?.body_template) {
    ElMessage.warning('没有模板可应用')
    return
  }

  let result = selectedWebhook.value.body_template

  // 替换自定义变量
  for (const [key, value] of Object.entries(variableValues)) {
    const pattern = new RegExp(`\\{\\{\\s*${key}\\s*\\}\\}`, 'g')
    result = result.replace(pattern, value || '')
  }

  triggerForm.request_body = result
  ElMessage.success('变量已应用到请求体')
}

const handleTrigger = async () => {
  try {
    await triggerFormRef.value.validate()
    triggering.value = true
    triggerResult.value = null

    let requestBody = null
    if (triggerForm.request_body) {
      try {
        requestBody = JSON.parse(triggerForm.request_body)
      } catch (e) {
        ElMessage.error('请求体不是有效的 JSON 格式')
        triggering.value = false
        return
      }
    }

    // 传递变量值到后端
    const res = await triggerWebhook({
      webhook_id: triggerForm.webhook_id,
      request_body: requestBody,
      variables: { ...variableValues }
    })

    triggerResult.value = {
      success: res.data.status === 'success',
      message: res.data.status === 'success'
        ? `请求成功，响应码: ${res.data.response_code}，历史记录 ID: ${res.data.id}`
        : `请求失败: ${res.data.error_message || '未知错误'}`
    }
    if (res.data.status === 'success') {
      ElMessage.success('请求已发送')
    } else {
      ElMessage.warning('请求发送但返回错误')
    }
    loadHistory()
  } catch (error) {
    triggerResult.value = {
      success: false,
      message: error.message || '请求失败'
    }
    ElMessage.error('请求失败')
  } finally {
    triggering.value = false
  }
}

const resetTriggerForm = () => {
  triggerForm.webhook_id = null
  triggerForm.request_body = ''
  triggerResult.value = null
  Object.keys(variableValues).forEach(key => delete variableValues[key])
}

const copyUrl = () => {
  if (selectedWebhook.value) {
    navigator.clipboard.writeText(selectedWebhook.value.url)
    ElMessage.success('已复制到剪贴板')
  }
}

const copyToClipboard = (text) => {
  if (text) {
    navigator.clipboard.writeText(text)
    ElMessage.success('已复制到剪贴板')
  }
}

const formatJson = () => {
  try {
    const parsed = JSON.parse(triggerForm.request_body)
    triggerForm.request_body = JSON.stringify(parsed, null, 2)
  } catch (e) {
    ElMessage.error('JSON 格式错误，无法格式化')
  }
}

const loadTemplateBody = () => {
  if (selectedWebhook.value && selectedWebhook.value.body_template) {
    triggerForm.request_body = selectedWebhook.value.body_template
    ElMessage.success('已加载模板')
  } else {
    triggerForm.request_body = JSON.stringify({
      "url": "{{article_url}}",
      "timestamp": "{{timestamp}}",
      "source": "knowledge-management"
    }, null, 2)
    ElMessage.success('已加载默认模板')
  }
}

const handleCreateConfig = () => {
  configDialogTitle.value = '新建配置'
  configActiveTab.value = 'basic'
  Object.assign(configForm, {
    id: null,
    name: '',
    url: '',
    method: 'POST',
    content_type: 'application/json',
    timeout: 30,
    description: '',
    is_active: true,
    headers: [],
    body_template: ''
  })
  configDialogVisible.value = true
}

const handleEditConfig = (row) => {
  configDialogTitle.value = '编辑配置'
  configActiveTab.value = 'basic'
  // 解析headers
  let headers = []
  if (row.headers) {
    try {
      const headersObj = typeof row.headers === 'string' ? JSON.parse(row.headers) : row.headers
      headers = Object.entries(headersObj).map(([key, value]) => ({ key, value }))
    } catch (e) {
      headers = []
    }
  }
  Object.assign(configForm, {
    ...row,
    headers,
    content_type: row.content_type || 'application/json',
    timeout: row.timeout || 30,
    body_template: row.body_template || ''
  })
  configDialogVisible.value = true
}

const handleTestConfig = (row) => {
  // 选中这个webhook并切换到触发区域
  triggerForm.webhook_id = row.id
  ElMessage.info('已选中该Webhook，请在左侧触发区域编辑请求体并发送')
}

const addHeader = () => {
  configForm.headers.push({ key: '', value: '' })
}

const removeHeader = (index) => {
  configForm.headers.splice(index, 1)
}

const formatConfigJson = () => {
  try {
    const parsed = JSON.parse(configForm.body_template)
    configForm.body_template = JSON.stringify(parsed, null, 2)
  } catch (e) {
    ElMessage.error('JSON 格式错误，无法格式化')
  }
}

const insertDefaultTemplate = () => {
  configForm.body_template = JSON.stringify({
    "url": "{{article_url}}",
    "timestamp": "{{timestamp}}",
    "webhook_name": "{{webhook_name}}",
    "date": "{{date}}",
    "source": "knowledge-management"
  }, null, 2)
}

const handleSubmitConfig = async () => {
  try {
    await configFormRef.value.validate()
    submittingConfig.value = true

    // 将headers数组转换为对象
    const headersObj = {}
    configForm.headers.forEach(h => {
      if (h.key && h.key.trim()) {
        headersObj[h.key.trim()] = h.value
      }
    })

    const submitData = {
      name: configForm.name,
      url: configForm.url,
      method: configForm.method,
      content_type: configForm.content_type,
      timeout: configForm.timeout,
      description: configForm.description,
      is_active: configForm.is_active,
      headers: JSON.stringify(headersObj),
      body_template: configForm.body_template
    }

    if (configForm.id) {
      await updateWebhookConfig(configForm.id, submitData)
      ElMessage.success('更新成功')
    } else {
      await createWebhookConfig(submitData)
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
  historyDetailTab.value = 'overview'
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

const getMethodType = (method) => {
  const map = {
    GET: 'success',
    POST: 'primary',
    PUT: 'warning',
    PATCH: 'warning',
    DELETE: 'danger'
  }
  return map[method] || 'info'
}

const getResponseCodeType = (code) => {
  if (!code) return 'info'
  if (code >= 200 && code < 300) return 'success'
  if (code >= 300 && code < 400) return 'warning'
  if (code >= 400) return 'danger'
  return 'info'
}

const getResponseCodeText = (code) => {
  if (!code) return ''
  const codeTexts = {
    200: 'OK',
    201: 'Created',
    204: 'No Content',
    301: 'Moved Permanently',
    302: 'Found',
    304: 'Not Modified',
    400: 'Bad Request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    408: 'Request Timeout',
    500: 'Internal Server Error',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout'
  }
  return codeTexts[code] || ''
}

const getDurationClass = (duration) => {
  if (!duration) return ''
  if (duration < 500) return 'duration-fast'
  if (duration < 2000) return 'duration-normal'
  return 'duration-slow'
}

const truncateUrl = (url) => {
  if (!url) return ''
  return url.length > 50 ? url.substring(0, 50) + '...' : url
}

const formatJsonDisplay = (jsonStr) => {
  if (!jsonStr) return ''
  try {
    const parsed = typeof jsonStr === 'string' ? JSON.parse(jsonStr) : jsonStr
    return JSON.stringify(parsed, null, 2)
  } catch (e) {
    return jsonStr
  }
}

const formatResponseBody = (body) => {
  if (!body) return ''
  // 尝试格式化JSON
  try {
    const parsed = JSON.parse(body)
    return JSON.stringify(parsed, null, 2)
  } catch (e) {
    // 如果不是JSON，直接返回原文
    return body
  }
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

.form-tip code {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  color: #409eff;
}

/* 下拉框样式 - 确保宽度足够 */
.full-width-select {
  width: 100%;
}

.filter-select {
  min-width: 150px;
}

.select-option-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-right: 10px;
}

.option-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: 10px;
}

/* JSON编辑器样式 */
.json-editor-wrapper {
  width: 100%;
}

.json-textarea :deep(.el-textarea__inner) {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.5;
}

.json-editor-actions {
  margin-top: 8px;
  display: flex;
  gap: 8px;
}

/* 请求头编辑器样式 */
.headers-editor {
  padding: 10px 0;
}

.headers-tip {
  margin-bottom: 15px;
}

.headers-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.header-item {
  display: flex;
  gap: 10px;
  align-items: center;
}

.header-key {
  flex: 1;
  max-width: 200px;
}

.header-value {
  flex: 2;
}

/* 请求体编辑器样式 */
.body-editor {
  padding: 10px 0;
}

.body-tip {
  margin-bottom: 15px;
}

.variables-list {
  margin-top: 8px;
  font-size: 13px;
}

.variables-list code {
  background: #ecf5ff;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  color: #409eff;
}

/* 历史详情样式 */
.detail-section {
  margin-bottom: 20px;
}

.detail-section h4 {
  margin-bottom: 10px;
  color: #303133;
  font-size: 14px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.section-header h4 {
  margin: 0;
  color: #303133;
  font-size: 14px;
}

/* URL显示样式 */
.url-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.url-text {
  word-break: break-all;
}

.url-box {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.method-tag {
  flex-shrink: 0;
}

.url-content {
  word-break: break-all;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
  font-size: 13px;
}

/* 响应状态样式 */
.response-status {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.status-text {
  color: #606266;
  font-size: 14px;
}

.duration-text {
  color: #909399;
  font-size: 13px;
  margin-left: auto;
}

/* 代码文本框样式 */
.code-textarea :deep(.el-textarea__inner) {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
  font-size: 12px;
  line-height: 1.5;
  background: #fafafa;
}

/* 耗时颜色 */
.duration-fast {
  color: #67c23a;
}

.duration-normal {
  color: #e6a23c;
}

.duration-slow {
  color: #f56c6c;
}

/* 文本截断 */
.truncate-text {
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 配置对话框样式 */
.config-dialog :deep(.el-dialog__body) {
  padding-top: 10px;
}

/* 历史详情对话框样式 */
.history-detail-dialog :deep(.el-dialog__body) {
  padding-top: 10px;
}
</style>

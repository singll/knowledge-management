<template>
  <div class="home-container">
    <el-card class="welcome-card">
      <template #header>
        <div class="card-header">
          <el-icon class="header-icon"><HomeFilled /></el-icon>
          <span>欢迎使用知识管理系统</span>
        </div>
      </template>
      
      <div class="stats-container">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic title="数据源总数" :value="stats.datasources">
              <template #prefix>
                <el-icon><Link /></el-icon>
              </template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="RSS 订阅源" :value="stats.rss">
              <template #prefix>
                <el-icon><Reading /></el-icon>
              </template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="标签数量" :value="stats.tags">
              <template #prefix>
                <el-icon><PriceTag /></el-icon>
              </template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="Webhook 配置" :value="stats.webhooks">
              <template #prefix>
                <el-icon><Connection /></el-icon>
              </template>
            </el-statistic>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <el-row :gutter="20" class="feature-cards">
      <el-col :span="8">
        <el-card shadow="hover" class="feature-card" @click="$router.push('/ragflow')">
          <el-icon class="feature-icon"><Upload /></el-icon>
          <h3>RagFlow 管理</h3>
          <p>上传文档到 RagFlow 知识库，支持字符串和批量上传</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="feature-card" @click="$router.push('/datasources')">
          <el-icon class="feature-icon"><Link /></el-icon>
          <h3>数据源管理</h3>
          <p>管理技术文章、资讯网站等数据源</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="feature-card" @click="$router.push('/webhook')">
          <el-icon class="feature-icon"><Connection /></el-icon>
          <h3>Webhook 工作流</h3>
          <p>触发 n8n 工作流，自动保存文章到知识库</p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { listTags } from '@/api/tags'
import { listDataSources } from '@/api/datasource'
import { listRSSFeeds } from '@/api/rss'
import { listWebhookConfigs } from '@/api/webhook'

const stats = ref({
  datasources: 0,
  rss: 0,
  tags: 0,
  webhooks: 0
})

const loadStats = async () => {
  try {
    const [tagsRes, dsRes, rssRes, whRes] = await Promise.all([
      listTags({ per_page: 1 }),
      listDataSources({ per_page: 1 }),
      listRSSFeeds({ per_page: 1 }),
      listWebhookConfigs({ per_page: 1 })
    ])
    
    stats.value = {
      tags: tagsRes.data?.pagination?.total || 0,
      datasources: dsRes.data?.pagination?.total || 0,
      rss: rssRes.data?.pagination?.total || 0,
      webhooks: whRes.data?.pagination?.total || 0
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.home-container {
  max-width: 1400px;
  margin: 0 auto;
}

.welcome-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: bold;
}

.header-icon {
  font-size: 24px;
  color: #409eff;
}

.stats-container {
  padding: 20px 0;
}

.feature-cards {
  margin-top: 20px;
}

.feature-card {
  cursor: pointer;
  text-align: center;
  padding: 20px;
  transition: all 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 15px;
}

.feature-card h3 {
  margin: 15px 0 10px;
  font-size: 18px;
  color: #303133;
}

.feature-card p {
  color: #909399;
  font-size: 14px;
  line-height: 1.6;
}
</style>

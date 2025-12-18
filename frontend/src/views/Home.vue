<template>
  <div class="home-container">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <div class="banner-content">
        <h1>知识管理系统</h1>
        <p>智能化的知识收集、整理与检索平台</p>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card" @click="$router.push('/datasets')">
          <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <el-icon><FolderOpened /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.datasets }}</span>
            <span class="stat-label">知识库</span>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card" @click="$router.push('/datasources')">
          <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <el-icon><Link /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.datasources }}</span>
            <span class="stat-label">数据源</span>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card" @click="$router.push('/rss')">
          <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <el-icon><Reading /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.rss }}</span>
            <span class="stat-label">RSS 订阅</span>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card" @click="$router.push('/tags')">
          <div class="stat-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
            <el-icon><PriceTag /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.tags }}</span>
            <span class="stat-label">标签</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <h2 class="section-title">快捷操作</h2>
    <el-row :gutter="20" class="feature-cards">
      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="hover" class="feature-card" @click="$router.push('/datasets')">
          <div class="feature-icon-wrapper" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <el-icon class="feature-icon"><FolderOpened /></el-icon>
          </div>
          <div class="feature-content">
            <h3>知识库管理</h3>
            <p>管理 RagFlow 知识库，上传文档，查看和管理已存储的知识内容</p>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="hover" class="feature-card" @click="$router.push('/datasources')">
          <div class="feature-icon-wrapper" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <el-icon class="feature-icon"><Link /></el-icon>
          </div>
          <div class="feature-content">
            <h3>数据源管理</h3>
            <p>管理技术文章、资讯网站等数据源，支持多种数据源类型</p>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="hover" class="feature-card" @click="$router.push('/webhook')">
          <div class="feature-icon-wrapper" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
            <el-icon class="feature-icon"><Connection /></el-icon>
          </div>
          <div class="feature-content">
            <h3>Webhook 工作流</h3>
            <p>触发 n8n 工作流，自动化处理文章并保存到知识库</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统功能 -->
    <h2 class="section-title">系统功能</h2>
    <el-row :gutter="20" class="quick-links">
      <el-col :xs="12" :sm="8" :md="6">
        <div class="quick-link-item" @click="$router.push('/rss')">
          <el-icon><Reading /></el-icon>
          <span>RSS 订阅管理</span>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="6">
        <div class="quick-link-item" @click="$router.push('/tags')">
          <el-icon><PriceTag /></el-icon>
          <span>标签管理</span>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="6">
        <div class="quick-link-item" @click="$router.push('/datasets?tab=mapping')">
          <el-icon><Share /></el-icon>
          <span>知识库映射</span>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="6">
        <div class="quick-link-item" @click="$router.push('/datasets?tab=upload')">
          <el-icon><Upload /></el-icon>
          <span>文档上传</span>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { listTags } from '@/api/tags'
import { listDataSources } from '@/api/datasource'
import { listRSSFeeds } from '@/api/rss'
import { listDatasets } from '@/api/ragflow'

const stats = ref({
  datasets: 0,
  datasources: 0,
  rss: 0,
  tags: 0
})

const loadStats = async () => {
  try {
    const [tagsRes, dsRes, rssRes, datasetsRes] = await Promise.all([
      listTags({ per_page: 1 }),
      listDataSources({ per_page: 1 }),
      listRSSFeeds({ per_page: 1 }),
      listDatasets({ page: 1, page_size: 100 })
    ])

    stats.value = {
      tags: tagsRes.data?.pagination?.total || 0,
      datasources: dsRes.data?.pagination?.total || 0,
      rss: rssRes.data?.pagination?.total || 0,
      datasets: datasetsRes.data?.data?.length || 0
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

/* 欢迎横幅 */
.welcome-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 40px;
  margin-bottom: 30px;
  color: #fff;
}

.banner-content h1 {
  font-size: 32px;
  font-weight: 600;
  margin-bottom: 10px;
}

.banner-content p {
  font-size: 16px;
  opacity: 0.9;
}

/* 统计卡片 */
.stats-row {
  margin-bottom: 30px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 12px;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  padding: 20px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.stat-icon .el-icon {
  font-size: 28px;
  color: #fff;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

/* 区域标题 */
.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
  padding-left: 12px;
  border-left: 4px solid #667eea;
}

/* 功能卡片 */
.feature-cards {
  margin-bottom: 30px;
}

.feature-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 12px;
  height: 100%;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.feature-card :deep(.el-card__body) {
  display: flex;
  align-items: flex-start;
  padding: 24px;
}

.feature-icon-wrapper {
  width: 60px;
  height: 60px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-right: 20px;
}

.feature-icon {
  font-size: 28px;
  color: #fff;
}

.feature-content {
  flex: 1;
}

.feature-content h3 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.feature-content p {
  font-size: 14px;
  color: #909399;
  margin: 0;
  line-height: 1.6;
}

/* 快捷链接 */
.quick-links {
  margin-bottom: 20px;
}

.quick-link-item {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  background: #fff;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  margin-bottom: 12px;
}

.quick-link-item:hover {
  background: #f5f7fa;
  transform: translateX(5px);
}

.quick-link-item .el-icon {
  font-size: 22px;
  color: #667eea;
  margin-right: 12px;
}

.quick-link-item span {
  font-size: 15px;
  color: #606266;
  font-weight: 500;
}

/* 响应式 */
@media (max-width: 768px) {
  .welcome-banner {
    padding: 24px;
  }

  .banner-content h1 {
    font-size: 24px;
  }

  .stat-card :deep(.el-card__body) {
    padding: 16px;
  }

  .stat-icon {
    width: 44px;
    height: 44px;
    margin-right: 12px;
  }

  .stat-icon .el-icon {
    font-size: 22px;
  }

  .stat-value {
    font-size: 22px;
  }

  .feature-card :deep(.el-card__body) {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .feature-icon-wrapper {
    margin-right: 0;
    margin-bottom: 16px;
  }
}
</style>

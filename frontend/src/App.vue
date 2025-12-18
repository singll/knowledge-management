<template>
  <div id="app">
    <el-container class="layout-container">
      <el-header class="app-header">
        <div class="header-content">
          <div class="logo">
            <el-icon><Document /></el-icon>
            <span>知识管理系统</span>
          </div>
          <el-menu
            mode="horizontal"
            :default-active="activeMenu"
            router
            class="header-menu"
          >
            <el-menu-item index="/">
              <el-icon><HomeFilled /></el-icon>
              <span>首页</span>
            </el-menu-item>
            <el-menu-item index="/datasets">
              <el-icon><FolderOpened /></el-icon>
              <span>知识库</span>
            </el-menu-item>
            <el-menu-item index="/datasources">
              <el-icon><Link /></el-icon>
              <span>数据源</span>
            </el-menu-item>
            <el-menu-item index="/rss">
              <el-icon><Reading /></el-icon>
              <span>RSS 订阅</span>
            </el-menu-item>
            <el-menu-item index="/tags">
              <el-icon><PriceTag /></el-icon>
              <span>标签管理</span>
            </el-menu-item>
            <el-menu-item index="/webhook">
              <el-icon><Connection /></el-icon>
              <span>Webhook</span>
            </el-menu-item>
          </el-menu>
        </div>
      </el-header>
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

#app {
  height: 100vh;
}

.layout-container {
  height: 100%;
}

.app-header {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0 20px;
  display: flex;
  align-items: center;
}

.header-content {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: bold;
  color: #409eff;
}

.logo .el-icon {
  font-size: 28px;
}

.header-menu {
  border: none;
  flex: 1;
  justify-content: flex-end;
}

.app-main {
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}

/* 全局下拉框样式修复 */
.el-select {
  min-width: 120px;
}

.el-select .el-input__wrapper {
  min-width: 100px;
}

.el-select .el-select__wrapper {
  min-width: 100px;
}

/* 确保下拉选项可见 */
.el-select-dropdown__item {
  padding: 0 20px;
  min-width: 100px;
}

/* 表单内的下拉框 */
.el-form-item .el-select {
  width: 100%;
}

/* 行内表单的下拉框 */
.el-form--inline .el-form-item .el-select {
  min-width: 120px;
  width: auto;
}
</style>

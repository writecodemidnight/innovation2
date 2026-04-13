<template>
  <div class="system-config-page">
    <div class="page-header">
      <h2>系统配置</h2>
    </div>

    <el-tabs type="border-card">
      <el-tab-pane label="基础配置">
        <el-form :model="basicConfig" label-width="150px" style="max-width: 600px">
          <el-form-item label="系统名称">
            <el-input v-model="basicConfig.systemName" />
          </el-form-item>
          <el-form-item label="系统Logo">
            <el-upload
              class="logo-uploader"
              action="/api/upload"
              :show-file-list="false"
              :on-success="handleLogoSuccess"
            >
              <img v-if="basicConfig.logo" :src="basicConfig.logo" class="logo-image" />
              <el-icon v-else class="logo-uploader-icon"><Plus /></el-icon>
            </el-upload>
          </el-form-item>
          <el-form-item label="备案号">
            <el-input v-model="basicConfig.icp" />
          </el-form-item>
          <el-form-item label="客服电话">
            <el-input v-model="basicConfig.servicePhone" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveBasicConfig">保存</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="审批配置">
        <el-form :model="approvalConfig" label-width="150px" style="max-width: 600px">
          <el-form-item label="活动自动审批">
            <el-switch v-model="approvalConfig.autoApproveActivity" />
          </el-form-item>
          <el-form-item label="资源自动审批">
            <el-switch v-model="approvalConfig.autoApproveResource" />
          </el-form-item>
          <el-form-item label="审批时限（小时）">
            <el-input-number v-model="approvalConfig.approvalTimeout" :min="1" :max="72" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveApprovalConfig">保存</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="通知配置">
        <el-form :model="notificationConfig" label-width="150px" style="max-width: 600px">
          <el-form-item label="开启邮件通知">
            <el-switch v-model="notificationConfig.enableEmail" />
          </el-form-item>
          <el-form-item label="开启短信通知">
            <el-switch v-model="notificationConfig.enableSms" />
          </el-form-item>
          <el-form-item label="审批提醒">
            <el-switch v-model="notificationConfig.approvalReminder" />
          </el-form-item>
          <el-form-item label="活动开始前提醒">
            <el-switch v-model="notificationConfig.activityReminder" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveNotificationConfig">保存</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="安全设置">
        <el-form :model="securityConfig" label-width="150px" style="max-width: 600px">
          <el-form-item label="登录失败锁定">
            <el-switch v-model="securityConfig.loginLock" />
          </el-form-item>
          <el-form-item label="最大失败次数">
            <el-input-number v-model="securityConfig.maxFailedAttempts" :min="3" :max="10" />
          </el-form-item>
          <el-form-item label="锁定时长（分钟）">
            <el-input-number v-model="securityConfig.lockDuration" :min="5" :max="60" />
          </el-form-item>
          <el-form-item label="会话超时（分钟）">
            <el-input-number v-model="securityConfig.sessionTimeout" :min="10" :max="120" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveSecurityConfig">保存</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue';
import { Plus } from '@element-plus/icons-vue';

const basicConfig = reactive({
  systemName: '校园社团活动评估系统',
  logo: '',
  icp: '',
  servicePhone: '',
});

const approvalConfig = reactive({
  autoApproveActivity: false,
  autoApproveResource: false,
  approvalTimeout: 24,
});

const notificationConfig = reactive({
  enableEmail: true,
  enableSms: false,
  approvalReminder: true,
  activityReminder: true,
});

const securityConfig = reactive({
  loginLock: true,
  maxFailedAttempts: 5,
  lockDuration: 30,
  sessionTimeout: 30,
});

function handleLogoSuccess(response: any) {
  basicConfig.logo = response.url;
}

function saveBasicConfig() {
  ElMessage.success('基础配置保存成功');
}

function saveApprovalConfig() {
  ElMessage.success('审批配置保存成功');
}

function saveNotificationConfig() {
  ElMessage.success('通知配置保存成功');
}

function saveSecurityConfig() {
  ElMessage.success('安全设置保存成功');
}
</script>

<style scoped lang="scss">
.system-config-page {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;

  h2 {
    margin: 0;
  }
}

.logo-uploader {
  :deep(.el-upload) {
    border: 1px dashed var(--el-border-color);
    border-radius: 6px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    transition: var(--el-transition-duration-fast);

    &:hover {
      border-color: var(--el-color-primary);
    }
  }
}

.logo-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  text-align: center;
  line-height: 178px;
}

.logo-image {
  width: 178px;
  height: 178px;
  display: block;
  object-fit: contain;
}
</style>

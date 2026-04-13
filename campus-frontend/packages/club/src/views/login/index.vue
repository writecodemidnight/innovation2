<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <el-icon size="64" color="#409EFF"><School /></el-icon>
        <h1 class="login-title">社团管理系统</h1>
        <p class="login-subtitle">校园社团活动效果评估与资源优化配置</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            size="large"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-button"
            :loading="userStore.loading"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <p>© 2025 校园社团活动评估系统</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { User, Lock } from '@element-plus/icons-vue';
import { useUserStore } from '@/stores/user';

const router = useRouter();
const userStore = useUserStore();
const formRef = ref();

const form = reactive({
  username: '',
  password: '',
});

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
};

const handleLogin = async () => {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;

  const success = await userStore.login(form);
  if (success) {
    ElMessage.success('登录成功');
    router.push('/');
  } else {
    ElMessage.error('登录失败，请检查用户名和密码');
  }
};
</script>

<style scoped lang="scss">
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-container {
  width: 420px;
  padding: 48px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-title {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin: 20px 0 8px;
}

.login-subtitle {
  font-size: 14px;
  color: #909399;
}

.login-form {
  .login-button {
    width: 100%;
    margin-top: 16px;
  }
}

.login-footer {
  text-align: center;
  margin-top: 32px;
  color: #909399;
  font-size: 12px;
}
</style>

<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <el-icon size="64" color="#00d4aa"><Monitor /></el-icon>
        <h1 class="login-title">管理控制台</h1>
        <p class="login-subtitle">校园社团活动效果评估与资源优化配置系统</p>
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
            placeholder="管理员账号"
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
        <p>© 2025 校园社团活动评估系统 · 管理后台</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { User, Lock, Monitor } from '@element-plus/icons-vue';
import { useUserStore } from '@/stores/user';

const router = useRouter();
const userStore = useUserStore();
const formRef = ref();

const form = reactive({
  username: '',
  password: '',
});

const rules = {
  username: [{ required: true, message: '请输入管理员账号', trigger: 'blur' }],
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
    ElMessage.error('登录失败，请检查账号和密码');
  }
};
</script>

<style scoped lang="scss">
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f1419 0%, #1a2332 100%);
}

.login-container {
  width: 420px;
  padding: 48px;
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-title {
  font-size: 28px;
  font-weight: 600;
  color: #fff;
  margin: 20px 0 8px;
}

.login-subtitle {
  font-size: 14px;
  color: #8b949e;
}

.login-form {
  :deep(.el-input__wrapper) {
    background: #0d1117;
    border: 1px solid #30363d;
    box-shadow: none;
  }

  :deep(.el-input__inner) {
    color: #c9d1d9;
  }

  .login-button {
    width: 100%;
    margin-top: 16px;
    background: #238636;
    border-color: #238636;

    &:hover {
      background: #2ea043;
      border-color: #2ea043;
    }
  }
}

.login-footer {
  text-align: center;
  margin-top: 32px;
  color: #6e7681;
  font-size: 12px;
}
</style>

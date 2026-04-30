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

        <el-form-item>
          <el-button
            size="large"
            class="register-button"
            @click="showRegisterDialog = true"
          >
            注册社团
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <p>© 2025 校园社团活动评估系统</p>
      </div>
    </div>

    <!-- 社团注册对话框 -->
    <el-dialog
      v-model="showRegisterDialog"
      title="注册新社团"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        label-width="100px"
      >
        <el-divider content-position="left">社团信息</el-divider>
        <el-form-item label="社团名称" prop="clubName">
          <el-input v-model="registerForm.clubName" placeholder="请输入社团名称" />
        </el-form-item>
        <el-form-item label="社团类别" prop="category">
          <el-select v-model="registerForm.category" placeholder="请选择社团类别" style="width: 100%">
            <el-option label="学术科技" value="ACADEMIC" />
            <el-option label="文化艺术" value="ARTS" />
            <el-option label="体育运动" value="SPORTS" />
            <el-option label="公益志愿" value="VOLUNTEER" />
            <el-option label="科技创新" value="TECHNOLOGY" />
            <el-option label="传统文化" value="CULTURE" />
            <el-option label="其他" value="OTHER" />
          </el-select>
        </el-form-item>
        <el-form-item label="社团描述" prop="description">
          <el-input
            v-model="registerForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入社团描述"
          />
        </el-form-item>
        <el-form-item label="指导教师" prop="facultyAdvisor">
          <el-input v-model="registerForm.facultyAdvisor" placeholder="请输入指导教师姓名" />
        </el-form-item>

        <el-divider content-position="left">社长账号</el-divider>
        <el-form-item label="社长账号" prop="presidentUsername">
          <el-input v-model="registerForm.presidentUsername" placeholder="请设置社长登录账号" />
        </el-form-item>
        <el-form-item label="登录密码" prop="presidentPassword">
          <el-input
            v-model="registerForm.presidentPassword"
            type="password"
            placeholder="请设置登录密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRegisterDialog = false">取消</el-button>
        <el-button type="primary" :loading="registerLoading" @click="handleRegister">
          注册
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { User, Lock } from '@element-plus/icons-vue';
import { useUserStore } from '@/stores/user';
import { apiClient, clearTokenCache } from '@campus/shared';

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

  try {
    await userStore.login(form);
    ElMessage.success('登录成功');
    router.push('/');
  } catch (error: any) {
    ElMessage.error(error.message || '登录失败，请检查用户名和密码');
  }
};

// 注册相关
const showRegisterDialog = ref(false);
const registerFormRef = ref();
const registerLoading = ref(false);

const registerForm = reactive({
  clubName: '',
  category: '',
  description: '',
  facultyAdvisor: '',
  presidentUsername: '',
  presidentPassword: '',
  confirmPassword: '',
});

const validateConfirmPassword = (rule: any, value: string, callback: Function) => {
  if (value !== registerForm.presidentPassword) {
    callback(new Error('两次输入的密码不一致'));
  } else {
    callback();
  }
};

const registerRules = {
  clubName: [{ required: true, message: '请输入社团名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择社团类别', trigger: 'change' }],
  presidentUsername: [
    { required: true, message: '请设置社长账号', trigger: 'blur' },
    { min: 4, message: '账号长度至少4个字符', trigger: 'blur' },
  ],
  presidentPassword: [
    { required: true, message: '请设置登录密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6个字符', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' },
  ],
};

const handleRegister = async () => {
  const valid = await registerFormRef.value?.validate().catch(() => false);
  if (!valid) return;

  registerLoading.value = true;
  try {
    const { confirmPassword, ...payload } = registerForm;

    // 注册前清除旧token，避免请求时带上旧token
    clearTokenCache();
    localStorage.removeItem('access_token');

    const response = await apiClient.post('/api/v1/auth/register/club', payload);

    // 保存token
    if (response.accessToken) {
      localStorage.setItem('access_token', response.accessToken);
      userStore.token = response.accessToken;
      userStore.userInfo = response.user;
    }

    ElMessage.success('社团注册成功！');
    showRegisterDialog.value = false;
    router.push('/');
  } catch (error: any) {
    ElMessage.error(error.message || '注册失败，请重试');
  } finally {
    registerLoading.value = false;
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

  .register-button {
    width: 100%;
    margin-top: 8px;
  }
}

.login-footer {
  text-align: center;
  margin-top: 32px;
  color: #909399;
  font-size: 12px;
}
</style>

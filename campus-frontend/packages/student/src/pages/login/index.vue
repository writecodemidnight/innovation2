<template>
  <view class="login-page">
    <view class="login-header">
      <image class="logo" src="/static/logo.png" mode="aspectFit" />
      <text class="title">校园社团活动</text>
      <text class="subtitle">发现精彩活动，记录成长足迹</text>
    </view>

    <view class="login-content">
      <!-- 微信登录按钮 -->
      <!-- #ifdef MP-WEIXIN -->
      <button
        class="wx-login-btn"
        @click="handleWxLogin"
        :loading="loading"
        :disabled="loading"
      >
        <uni-icons type="weixin" size="24" color="#fff" />
        <text>微信一键登录</text>
      </button>
      <!-- #endif -->

      <!-- H5/开发环境测试登录 -->
      <!-- #ifdef H5 -->
      <view class="test-login">
        <text class="section-title">开发测试登录</text>
        <input
          v-model="form.username"
          class="input"
          placeholder="用户名"
          type="text"
        />
        <input
          v-model="form.password"
          class="input"
          placeholder="密码"
          type="password"
        />
        <button
          class="login-btn"
          @click="handleLogin"
          :loading="loading"
          :disabled="loading"
        >
          登录
        </button>
        <button
          class="register-btn"
          @click="showRegister = true"
        >
          注册账号
        </button>
      </view>
      <!-- #endif -->

      <text class="tips">
        登录即表示您同意《用户协议》和《隐私政策》
      </text>
    </view>
  </view>

  <!-- 注册弹窗 -->
  <uni-popup ref="registerPopup" type="center" @change="onPopupChange">
    <view class="register-popup">
      <view class="register-header">
        <text class="register-title">学生注册</text>
        <text class="register-close" @click="closeRegister">×</text>
      </view>

      <view class="register-form">
        <input
          v-model="registerForm.studentId"
          class="register-input"
          placeholder="学号"
          type="text"
        />
        <input
          v-model="registerForm.username"
          class="register-input"
          placeholder="用户名"
          type="text"
        />
        <input
          v-model="registerForm.nickname"
          class="register-input"
          placeholder="昵称（可选）"
          type="text"
        />
        <input
          v-model="registerForm.password"
          class="register-input"
          placeholder="密码"
          type="password"
        />
        <input
          v-model="registerForm.confirmPassword"
          class="register-input"
          placeholder="确认密码"
          type="password"
        />
        <input
          v-model="registerForm.phone"
          class="register-input"
          placeholder="手机号（可选）"
          type="number"
        />
        <input
          v-model="registerForm.email"
          class="register-input"
          placeholder="邮箱（可选）"
          type="text"
        />

        <button
          class="register-submit-btn"
          @click="handleRegister"
          :loading="registerLoading"
          :disabled="registerLoading"
        >
          注册
        </button>
      </view>
    </view>
  </uni-popup>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useUserStore } from '@/stores/user';
import { apiClient, Endpoints } from '@campus/shared';

const userStore = useUserStore();
const loading = ref(false);
const registerLoading = ref(false);
const showRegister = ref(false);
const registerPopup = ref<any>(null);

// H5测试登录表单
const form = ref({
  username: 'student1',
  password: 'admin123',
});

// 注册表单
const registerForm = ref({
  studentId: '',
  username: '',
  nickname: '',
  password: '',
  confirmPassword: '',
  phone: '',
  email: '',
});

function onPopupChange(e: any) {
  if (!e.show) {
    showRegister.value = false;
  }
}

function closeRegister() {
  registerPopup.value?.close?.();
  showRegister.value = false;
}

// 监听showRegister变化
function openRegister() {
  showRegister.value = true;
  registerPopup.value?.open?.();
}

async function handleRegister() {
  // 表单验证
  if (!registerForm.value.studentId) {
    uni.showToast({ title: '请输入学号', icon: 'none' });
    return;
  }
  if (!registerForm.value.username) {
    uni.showToast({ title: '请输入用户名', icon: 'none' });
    return;
  }
  if (registerForm.value.username.length < 4) {
    uni.showToast({ title: '用户名至少4个字符', icon: 'none' });
    return;
  }
  if (!registerForm.value.password) {
    uni.showToast({ title: '请输入密码', icon: 'none' });
    return;
  }
  if (registerForm.value.password.length < 6) {
    uni.showToast({ title: '密码至少6个字符', icon: 'none' });
    return;
  }
  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    uni.showToast({ title: '两次输入的密码不一致', icon: 'none' });
    return;
  }

  registerLoading.value = true;
  try {
    const { confirmPassword, ...payload } = registerForm.value;
    const response: any = await apiClient.post('/api/v1/auth/register/student', payload);

    if (response.accessToken) {
      uni.setStorageSync('access_token', response.accessToken);
      userStore.token = response.accessToken;
      userStore.userInfo = response.user;
    }

    uni.showToast({
      title: '注册成功',
      icon: 'success',
    });

    closeRegister();

    setTimeout(() => {
      uni.switchTab({ url: '/pages/index/index' });
    }, 500);
  } catch (error: any) {
    console.error('注册失败:', error);
    uni.showToast({
      title: error.message || '注册失败',
      icon: 'none',
    });
  } finally {
    registerLoading.value = false;
  }
}

/**
 * 微信小程序登录
 */
async function handleWxLogin() {
  // #ifdef MP-WEIXIN
  loading.value = true;

  try {
    // 1. 获取微信登录 code
    const [loginErr, loginRes] = await uni.login({
      provider: 'weixin',
    });

    if (loginErr || !loginRes?.code) {
      throw new Error(loginErr?.errMsg || '获取微信登录凭证失败');
    }

    console.log('微信登录 code:', loginRes.code);

    // 2. 调用后端登录接口
    const success = await userStore.wxLogin(loginRes.code);

    if (success) {
      uni.showToast({
        title: '登录成功',
        icon: 'success',
      });

      // 3. 登录成功，跳转到首页
      setTimeout(() => {
        uni.switchTab({ url: '/pages/index/index' });
      }, 500);
    } else {
      throw new Error('登录失败');
    }
  } catch (error: any) {
    console.error('微信登录失败:', error);
    uni.showToast({
      title: error.message || '登录失败',
      icon: 'none',
    });
  } finally {
    loading.value = false;
  }
  // #endif
}

/**
 * 账号密码登录（H5测试用）
 */
async function handleLogin() {
  // #ifdef H5
  if (!form.value.username || !form.value.password) {
    uni.showToast({
      title: '请输入用户名和密码',
      icon: 'none',
    });
    return;
  }

  loading.value = true;

  try {
    const success = await userStore.login({
      username: form.value.username,
      password: form.value.password,
    });

    if (success) {
      uni.showToast({
        title: '登录成功',
        icon: 'success',
      });

      setTimeout(() => {
        uni.switchTab({ url: '/pages/index/index' });
      }, 500);
    } else {
      throw new Error('登录失败');
    }
  } catch (error: any) {
    console.error('登录失败:', error);
    uni.showToast({
      title: error.message || '登录失败',
      icon: 'none',
    });
  } finally {
    loading.value = false;
  }
  // #endif
}
</script>

<style scoped lang="scss">
.login-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #e6f2ff 0%, #f5f5f5 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40rpx;
}

.login-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 120rpx;
  margin-bottom: 80rpx;
}

.logo {
  width: 180rpx;
  height: 180rpx;
  margin-bottom: 30rpx;
}

.title {
  font-size: 48rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 16rpx;
}

.subtitle {
  font-size: 28rpx;
  color: #666;
}

.login-content {
  width: 100%;
  max-width: 600rpx;
}

.wx-login-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
  background: #07c160;
  color: #fff;
  border-radius: 12rpx;
  padding: 30rpx 0;
  font-size: 32rpx;
  font-weight: 500;
  border: none;
  margin-bottom: 40rpx;

  &::after {
    border: none;
  }

  &[disabled] {
    opacity: 0.6;
  }
}

.test-login {
  background: #fff;
  border-radius: 16rpx;
  padding: 40rpx;
  margin-bottom: 40rpx;

  .section-title {
    display: block;
    font-size: 32rpx;
    font-weight: 600;
    color: #333;
    margin-bottom: 30rpx;
    text-align: center;
  }

  .input {
    height: 90rpx;
    border: 2rpx solid #e5e5e5;
    border-radius: 12rpx;
    padding: 0 24rpx;
    font-size: 30rpx;
    margin-bottom: 24rpx;

    &:focus {
      border-color: #1989fa;
    }
  }

  .login-btn {
    background: #1989fa;
    color: #fff;
    border-radius: 12rpx;
    padding: 28rpx 0;
    font-size: 32rpx;
    font-weight: 500;
    border: none;

    &::after {
      border: none;
    }

    &[disabled] {
      opacity: 0.6;
    }
  }

  .register-btn {
    background: #fff;
    color: #1989fa;
    border: 2rpx solid #1989fa;
    border-radius: 12rpx;
    padding: 28rpx 0;
    font-size: 32rpx;
    font-weight: 500;
    margin-top: 24rpx;

    &::after {
      border: none;
    }
  }
}

// 注册弹窗样式
.register-popup {
  background: #fff;
  border-radius: 16rpx;
  width: 600rpx;
  max-height: 900rpx;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.register-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx 40rpx;
  border-bottom: 2rpx solid #eee;

  .register-title {
    font-size: 36rpx;
    font-weight: 600;
    color: #333;
  }

  .register-close {
    font-size: 48rpx;
    color: #999;
    line-height: 1;
    padding: 0 10rpx;
  }
}

.register-form {
  padding: 40rpx;
  max-height: 700rpx;
  overflow-y: auto;
}

.register-input {
  height: 90rpx;
  border: 2rpx solid #e5e5e5;
  border-radius: 12rpx;
  padding: 0 24rpx;
  font-size: 30rpx;
  margin-bottom: 24rpx;

  &:focus {
    border-color: #1989fa;
  }
}

.register-submit-btn {
  background: #1989fa;
  color: #fff;
  border-radius: 12rpx;
  padding: 28rpx 0;
  font-size: 32rpx;
  font-weight: 500;
  border: none;
  margin-top: 16rpx;

  &::after {
    border: none;
  }

  &[disabled] {
    opacity: 0.6;
  }
}

.tips {
  display: block;
  text-align: center;
  font-size: 24rpx;
  color: #999;
  margin-top: 40rpx;
}
</style>

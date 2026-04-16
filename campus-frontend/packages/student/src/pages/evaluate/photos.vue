<template>
  <view class="photos-page">
    <!-- 活动信息 -->
    <view class="activity-info card">
      <text class="info-text">{{ activity.title }}</text>
    </view>

    <!-- 照片上传 -->
    <view class="upload-section card">
      <view class="section-header">
        <text class="section-title">上传活动照片</text>
        <text class="section-subtitle">记录精彩瞬间</text>
      </view>

      <view class="photo-grid">
        <view
          v-for="(photo, index) in photos"
          :key="index"
          class="photo-item"
        >
          <image :src="photo" mode="aspectFill" @click="previewPhoto(index)" />
          <view class="delete-btn" @click.stop="removePhoto(index)">
            <uni-icons type="close" size="16" color="#fff" />
          </view>
        </view>
        <view v-if="photos.length < 9" class="upload-btn" @click="choosePhoto">
          <uni-icons type="camera" size="40" color="#999" />
          <text class="upload-text">上传照片</text>
          <text class="upload-count">{{ photos.length }}/9</text>
        </view>
      </view>
    </view>

    <!-- 描述输入 -->
    <view class="desc-section card">
      <view class="section-title">添加描述</view>
      <textarea
        v-model="description"
        class="desc-input"
        placeholder="分享你的活动体验..."
        maxlength="200"
      />
      <view class="word-count">{{ description.length }}/200</view>
    </view>

    <!-- 提交按钮 -->
    <view class="submit-bar">
      <button class="submit-btn" :disabled="photos.length === 0" @click="submit">
        上传分享
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

interface Activity {
  id: number;
  title: string;
}

const activity = ref<Activity>({
  id: 1,
  title: '科技创新讲座：AI前沿技术探索',
});

const photos = ref<string[]>([]);
const description = ref('');

onMounted(() => {
  const pages = getCurrentPages();
  const currentPage = pages[pages.length - 1];
  const { id } = currentPage.$page?.options || {};
  if (id) {
    console.log('上传照片活动ID:', id);
  }
});

function choosePhoto() {
  uni.chooseImage({
    count: 9 - photos.value.length,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: (res) => {
      photos.value.push(...res.tempFilePaths);
    },
  });
}

function removePhoto(index: number) {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除这张照片吗？',
    success: (res) => {
      if (res.confirm) {
        photos.value.splice(index, 1);
      }
    },
  });
}

function previewPhoto(index: number) {
  uni.previewImage({
    urls: photos.value,
    current: photos.value[index],
  });
}

async function submit() {
  if (photos.value.length === 0) {
    uni.showToast({ title: '请至少上传一张照片', icon: 'none' });
    return;
  }

  uni.showLoading({ title: '上传中...' });

  try {
    const uploadedUrls: string[] = [];

    for (const photo of photos.value) {
      const url = await uploadImage(photo);
      if (url) uploadedUrls.push(url);
    }

    if (uploadedUrls.length === 0) {
      throw new Error('图片上传失败');
    }

    uni.hideLoading();
    uni.showToast({ title: '上传成功', icon: 'success' });

    // 返回上传后的图片URL给上一页
    const pages = getCurrentPages();
    const prevPage = pages[pages.length - 2] as any;
    if (prevPage && prevPage.$vm) {
      prevPage.$vm.handlePhotosUploaded?.(uploadedUrls);
    }

    setTimeout(() => {
      uni.navigateBack();
    }, 1500);
  } catch (error: any) {
    uni.hideLoading();
    uni.showToast({ title: error.message || '上传失败', icon: 'none' });
  }
}

async function uploadImage(filePath: string): Promise<string | null> {
  return new Promise((resolve) => {
    uni.uploadFile({
      url: '/api/upload/image',
      filePath,
      name: 'file',
      header: {
        Authorization: `Bearer ${uni.getStorageSync('access_token')}`,
      },
      success: (res) => {
        if (res.statusCode === 200) {
          try {
            const data = JSON.parse(res.data);
            resolve(data.url || null);
          } catch {
            resolve(null);
          }
        } else {
          resolve(null);
        }
      },
      fail: () => resolve(null),
    });
  });
}
</script>

<style scoped lang="scss">
.photos-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 120rpx;
}

.activity-info {
  margin: 20rpx;
  padding: 20rpx;
}

.info-text {
  font-size: 28rpx;
  color: #666;
}

.upload-section {
  margin: 20rpx;
  padding: 30rpx;
}

.section-header {
  margin-bottom: 30rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  display: block;
  margin-bottom: 8rpx;
}

.section-subtitle {
  font-size: 26rpx;
  color: #999;
}

.photo-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
}

.photo-item {
  position: relative;
  width: 200rpx;
  height: 200rpx;

  image {
    width: 100%;
    height: 100%;
    border-radius: 12rpx;
  }
}

.delete-btn {
  position: absolute;
  top: -10rpx;
  right: -10rpx;
  width: 40rpx;
  height: 40rpx;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-btn {
  width: 200rpx;
  height: 200rpx;
  background: #f8f8f8;
  border-radius: 12rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  border: 2rpx dashed #ddd;
}

.upload-text {
  font-size: 26rpx;
  color: #666;
}

.upload-count {
  font-size: 24rpx;
  color: #999;
}

.desc-section {
  margin: 20rpx;
  padding: 30rpx;
}

.desc-input {
  width: 100%;
  height: 160rpx;
  padding: 20rpx;
  background: #f8f8f8;
  border-radius: 12rpx;
  font-size: 28rpx;
  margin-top: 20rpx;
  box-sizing: border-box;
}

.word-count {
  text-align: right;
  font-size: 24rpx;
  color: #999;
  margin-top: 8rpx;
}

.submit-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 20rpx 40rpx;
  padding-bottom: calc(20rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  background: #fff;
  box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.submit-btn {
  background: linear-gradient(135deg, #1989fa 0%, #096dd9 100%);
  color: #fff;
  border-radius: 44rpx;
  font-size: 32rpx;
  font-weight: 500;
  border: none;

  &:disabled {
    background: #ccc;
  }
}
</style>

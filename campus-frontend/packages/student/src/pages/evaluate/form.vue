<template>
  <view class="evaluate-page">
    <!-- 活动信息 -->
    <view class="activity-info card">
      <image class="activity-image" :src="activity.coverImageUrl" mode="aspectFill" />
      <view class="activity-content">
        <view class="activity-title">{{ activity.title }}</view>
        <view class="activity-club">{{ activity.clubName }}</view>
      </view>
    </view>

    <!-- 评价表单 -->
    <view class="evaluate-form card">
      <view class="form-item">
        <view class="item-label">总体评分</view>
        <uni-rate v-model="form.rating" :max="5" :value="5" />
      </view>

      <view class="form-item">
        <view class="item-label">活动组织</view>
        <uni-rate v-model="form.organizationRating" :max="5" :value="5" />
      </view>

      <view class="form-item">
        <view class="item-label">活动内容</view>
        <uni-rate v-model="form.contentRating" :max="5" :value="5" />
      </view>

      <view class="form-item">
        <view class="item-label">评价内容</view>
        <textarea
          v-model="form.comment"
          class="comment-input"
          placeholder="请输入您的评价内容..."
          maxlength="500"
        />
        <view class="word-count">{{ form.comment.length }}/500</view>
      </view>

      <view class="form-item">
        <view class="item-label">上传照片（可选）</view>
        <view class="photo-upload">
          <view
            v-for="(photo, index) in form.photos"
            :key="index"
            class="photo-item"
          >
            <image :src="photo" mode="aspectFill" />
            <view class="delete-btn" @click="removePhoto(index)">
              <uni-icons type="close" size="16" color="#fff" />
            </view>
          </view>
          <view v-if="form.photos.length < 6" class="upload-btn" @click="choosePhoto">
            <uni-icons type="camera" size="32" color="#999" />
            <text>{{ form.photos.length }}/6</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 提交按钮 -->
    <view class="submit-bar">
      <button class="submit-btn" :disabled="!canSubmit" @click="submit">
        提交评价
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';

interface Activity {
  id: number;
  title: string;
  clubName: string;
  coverImageUrl: string;
}

const activity = ref<Activity>({
  id: 1,
  title: '科技创新讲座：AI前沿技术探索',
  clubName: '科技创新社',
  coverImageUrl: 'https://picsum.photos/400/200',
});

const form = ref({
  rating: 5,
  organizationRating: 5,
  contentRating: 5,
  comment: '',
  photos: [] as string[],
});

const canSubmit = computed(() => {
  return form.value.rating > 0 && form.value.comment.trim().length > 0;
});

onMounted(() => {
  // 获取活动ID
  const pages = getCurrentPages();
  const currentPage = pages[pages.length - 1];
  const { id } = currentPage.$page?.options || {};
  if (id) {
    console.log('评价活动ID:', id);
  }
});

function choosePhoto() {
  uni.chooseImage({
    count: 6 - form.value.photos.length,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: (res) => {
      form.value.photos.push(...res.tempFilePaths);
    },
  });
}

function removePhoto(index: number) {
  form.value.photos.splice(index, 1);
}

function submit() {
  if (!canSubmit.value) return;

  uni.showModal({
    title: '确认提交',
    content: '确定要提交评价吗？',
    success: (res) => {
      if (res.confirm) {
        // TODO: 调用提交API
        uni.showToast({ title: '评价成功', icon: 'success' });
        setTimeout(() => {
          uni.navigateBack();
        }, 1500);
      }
    },
  });
}
</script>

<style scoped lang="scss">
.evaluate-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 120rpx;
}

.activity-info {
  display: flex;
  align-items: center;
  padding: 20rpx;
  margin: 20rpx;
}

.activity-image {
  width: 120rpx;
  height: 120rpx;
  border-radius: 12rpx;
  margin-right: 20rpx;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 8rpx;
}

.activity-club {
  font-size: 26rpx;
  color: #666;
}

.evaluate-form {
  margin: 20rpx;
  padding: 30rpx;
}

.form-item {
  margin-bottom: 40rpx;

  &:last-child {
    margin-bottom: 0;
  }
}

.item-label {
  font-size: 28rpx;
  color: #333;
  margin-bottom: 16rpx;
  font-weight: 500;
}

.comment-input {
  width: 100%;
  height: 200rpx;
  padding: 20rpx;
  background: #f8f8f8;
  border-radius: 12rpx;
  font-size: 28rpx;
  box-sizing: border-box;
}

.word-count {
  text-align: right;
  font-size: 24rpx;
  color: #999;
  margin-top: 8rpx;
}

.photo-upload {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
}

.photo-item {
  position: relative;
  width: 180rpx;
  height: 180rpx;

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
  width: 180rpx;
  height: 180rpx;
  background: #f8f8f8;
  border-radius: 12rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  border: 2rpx dashed #ddd;

  text {
    font-size: 24rpx;
    color: #999;
  }
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

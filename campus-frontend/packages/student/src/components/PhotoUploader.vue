<template>
  <view class="photo-uploader">
    <view class="uploader-header">
      <text class="uploader-title">{{ title }}</text>
      <text class="uploader-count">{{ files.length }}/{{ maxCount }}</text>
    </view>
    <view class="photo-grid">
      <view
        v-for="(file, index) in files"
        :key="index"
        class="photo-item"
      >
        <image class="photo-image" :src="file.url" mode="aspectFill" />
        <view class="photo-delete" @click="removePhoto(index)">
          <van-icon name="clear" size="40rpx" color="#fff" />
        </view>
      </view>
      <view
        v-if="files.length < maxCount"
        class="photo-add"
        @click="choosePhoto"
      >
        <van-icon name="plus" size="48rpx" color="#ccc" />
        <text class="add-text">添加照片</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue';

interface PhotoFile {
  url: string;
  file?: File;
}

const props = withDefaults(defineProps<{
  title?: string;
  maxCount?: number;
  maxSize?: number; // MB
}>(), {
  title: '上传照片',
  maxCount: 9,
  maxSize: 10,
});

const emit = defineEmits<{
  change: [files: PhotoFile[]];
}>();

const files = ref<PhotoFile[]>([]);

// 选择照片
function choosePhoto() {
  uni.chooseImage({
    count: props.maxCount - files.value.length,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: (res) => {
      const newFiles = res.tempFilePaths.map(url => ({ url }));
      files.value.push(...newFiles);
      emit('change', files.value);
    },
  });
}

// 移除照片
function removePhoto(index: number) {
  files.value.splice(index, 1);
  emit('change', files.value);
}
</script>

<style scoped lang="scss">
.photo-uploader {
  padding: 24rpx;
  background: #fff;
  border-radius: 16rpx;
}

.uploader-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.uploader-title {
  font-size: 30rpx;
  font-weight: 500;
  color: #333;
}

.uploader-count {
  font-size: 26rpx;
  color: #999;
}

.photo-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.photo-item {
  position: relative;
  width: calc((100% - 48rpx) / 3);
  aspect-ratio: 1;
  border-radius: 12rpx;
  overflow: hidden;
}

.photo-image {
  width: 100%;
  height: 100%;
}

.photo-delete {
  position: absolute;
  top: 8rpx;
  right: 8rpx;
  width: 40rpx;
  height: 40rpx;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.photo-add {
  width: calc((100% - 48rpx) / 3);
  aspect-ratio: 1;
  border: 2rpx dashed #ddd;
  border-radius: 12rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.add-text {
  font-size: 24rpx;
  color: #999;
  margin-top: 8rpx;
}
</style>

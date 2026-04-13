<template>
  <view class="rating-stars">
    <view class="rating-header">
      <text class="rating-label">{{ label }}</text>
      <text class="rating-score">{{ modelValue }}分</text>
    </view>
    <view class="rating-desc">{{ description }}</view>
    <van-rate
      :model-value="modelValue"
      @update:model-value="$emit('update:modelValue', $event)"
      :size="size"
      :color="color"
      :void-color="voidColor"
      :allow-half="allowHalf"
    />
  </view>
</template>

<script setup lang="ts">
defineProps<{
  modelValue: number;
  label: string;
  description?: string;
  size?: number;
  color?: string;
  voidColor?: string;
  allowHalf?: boolean;
}>();

defineEmits<{
  'update:modelValue': [value: number];
}>();
</script>

<style scoped lang="scss">
.rating-stars {
  padding: 24rpx 0;
  border-bottom: 1rpx solid #f0f0f0;

  &:last-child {
    border-bottom: none;
  }
}

.rating-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8rpx;
}

.rating-label {
  font-size: 30rpx;
  font-weight: 500;
  color: #333;
}

.rating-score {
  font-size: 32rpx;
  font-weight: 600;
  color: #ff9900;
}

.rating-desc {
  font-size: 24rpx;
  color: #999;
  margin-bottom: 16rpx;
}
</style>

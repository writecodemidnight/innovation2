<template>
  <view class="star-rating">
    <view class="rating-header">
      <text class="rating-label">{{ label }}</text>
      <text class="rating-score">{{ displayValue }}分</text>
    </view>
    <view class="stars-wrapper">
      <view
        v-for="index in 10"
        :key="index"
        class="star-item"
        @click="handleStarClick(index)"
      >
        <text
          class="star-icon"
          :class="getStarClass(index)"
        >★</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  modelValue: number;
  label: string;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: number];
}>();

const displayValue = computed(() => {
  return props.modelValue.toFixed(1);
});

function handleStarClick(index: number) {
  // index 1-10 对应 0.5-5分
  const value = index * 0.5;
  emit('update:modelValue', value);
}

function getStarClass(index: number) {
  const threshold = index * 0.5;
  if (props.modelValue >= threshold) {
    return 'full';
  } else if (props.modelValue >= threshold - 0.25) {
    return 'half';
  }
  return 'empty';
}
</script>

<style scoped lang="scss">
.star-rating {
  margin-bottom: 32rpx;
}

.rating-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.rating-label {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
}

.rating-score {
  font-size: 32rpx;
  color: #ff9900;
  font-weight: 600;
}

.stars-wrapper {
  display: flex;
  gap: 8rpx;
}

.star-item {
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.star-icon {
  font-size: 44rpx;
  line-height: 1;
  transition: all 0.2s;

  &.full {
    color: #ff9900;
  }

  &.half {
    color: #ffcc00;
    opacity: 0.8;
  }

  &.empty {
    color: #ddd;
  }
}
</style>

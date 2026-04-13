package com.campusclub.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * 调度配置
 * 启用Spring的定时任务功能
 */
@Configuration
@EnableScheduling
public class SchedulingConfig {
    // 调度配置类，启用@EnableScheduling即可
    // 具体的定时任务在各自的组件中定义
}

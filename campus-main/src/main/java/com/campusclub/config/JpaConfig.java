package com.campusclub.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.transaction.annotation.EnableTransactionManagement;

@Configuration
@EnableTransactionManagement
@EnableJpaRepositories(basePackages = "com.campusclub.**.repository")
public class JpaConfig {
    // JPA配置已通过注解完成
    // 注意：@EnableJpaAuditing 在 CampusClubApplication 中定义
}
package com.campusclub.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.tags.Tag;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.Arrays;

/**
 * Swagger/OpenAPI配置
 */
@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("校园社团活动评估系统API")
                        .version("1.0.0")
                        .description("校园社团活动评估系统后端API文档")
                        .contact(new Contact()
                                .name("Campus Club Team")
                                .email("support@campusclub.com"))
                        .license(new License()
                                .name("Apache 2.0")
                                .url("https://www.apache.org/licenses/LICENSE-2.0")))
                .tags(Arrays.asList(
                        new Tag().name("活动管理").description("社团活动的创建、查询、更新、删除"),
                        new Tag().name("评估管理").description("活动评估和评分相关接口"),
                        new Tag().name("资源管理").description("场地、设备等资源预约管理"),
                        new Tag().name("算法服务").description("AI算法服务代理接口"),
                        new Tag().name("用户管理").description("用户信息和权限管理"),
                        new Tag().name("系统监控").description("系统健康检查和监控接口")
                ));
    }
}

package com.campusclub.user.infrastructure.external;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Data
@Component
@ConfigurationProperties(prefix = "wechat.mp")
public class WechatMpProperties {
    private String appId;
    private String secret;
}

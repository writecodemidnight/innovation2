package com.campusclub.user.infrastructure.external;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

@Slf4j
@Component
@RequiredArgsConstructor
public class WechatMpClient {

    private static final String AUTH_CODE2SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session";

    private final WechatMpProperties properties;
    private final RestTemplate restTemplate = new RestTemplate();

    public WechatSessionResponse code2Session(String code) {
        String url = UriComponentsBuilder.fromHttpUrl(AUTH_CODE2SESSION_URL)
                .queryParam("appid", properties.getAppId())
                .queryParam("secret", properties.getSecret())
                .queryParam("js_code", code)
                .queryParam("grant_type", "authorization_code")
                .toUriString();

        log.info("Requesting WeChat session with code: {}", code);

        WechatSessionResponse response = restTemplate.getForObject(url, WechatSessionResponse.class);

        if (response != null && response.getErrcode() != null && response.getErrcode() != 0) {
            log.error("WeChat API error: {} - {}", response.getErrcode(), response.getErrmsg());
            throw new RuntimeException("微信登录失败: " + response.getErrmsg());
        }

        return response;
    }
}

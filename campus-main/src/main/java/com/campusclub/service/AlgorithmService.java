package com.campusclub.service;

import com.campusclub.dto.AlgorithmRequest;
import com.campusclub.dto.AlgorithmResponse;
import com.campusclub.exception.AlgorithmException;
import com.campusclub.exception.AlgorithmTimeoutException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.client.HttpClientErrorException;

import java.time.Duration;
import java.util.Map;
import java.util.concurrent.TimeoutException;

@Service
@RequiredArgsConstructor
@Slf4j
public class AlgorithmService {

    private final RestTemplate restTemplate;
    private final RedisTemplate<String, Object> redisTemplate;

    @Value("${algorithm.service.url:http://algorithm-service:8000}")
    private String algorithmServiceUrl;

    @Value("${algorithm.timeout.seconds:30}")
    private int timeoutSeconds;

    @Value("${algorithm.retry.count:3}")
    private int maxRetries;

    @Value("${algorithm.cache.ttl.standard:600}")
    private long standardCacheTtl;

    @Value("${algorithm.cache.ttl.extended:3600}")
    private long extendedCacheTtl;

    @Value("${algorithm.cache.ttl.medium:1800}")
    private long mediumCacheTtl;

    public AlgorithmResponse executeWithRetry(AlgorithmRequest request) {
        int retryCount = 0;
        long retryDelayMs = 1000;

        while (retryCount <= maxRetries) {
            try {
                // 尝试从缓存获取结果
                String cacheKey = generateCacheKey(request);
                AlgorithmResponse cachedResponse = getFromCache(cacheKey);
                if (cachedResponse != null) {
                    log.info("从缓存获取算法结果: {}", request.getAlgorithmType());
                    return cachedResponse;
                }

                // 调用算法服务
                AlgorithmResponse response = executeAlgorithm(request);

                // 缓存结果
                cacheResponse(cacheKey, response, getCacheTTL(request.getAlgorithmType()));

                return response;

            } catch (RuntimeException e) {
                // 检查是否是包装了TimeoutException的RuntimeException
                if (e.getCause() instanceof TimeoutException) {
                    retryCount++;
                    if (retryCount > maxRetries) {
                        throw new AlgorithmTimeoutException(
                            String.format("算法%s执行超时，重试%d次后失败",
                            request.getAlgorithmType(), maxRetries));
                    }

                    log.warn("算法执行超时，第{}次重试", retryCount);
                    try {
                        Thread.sleep(retryDelayMs * retryCount);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        throw new AlgorithmException("重试被中断", ie);
                    }
                } else {
                    throw new AlgorithmException("算法执行失败", e);
                }
            } catch (Exception e) {
                throw new AlgorithmException("算法执行失败", e);
            }
        }

        throw new AlgorithmException("算法执行失败，已达到最大重试次数");
    }

    private AlgorithmResponse executeAlgorithm(AlgorithmRequest request) {
        String url = algorithmServiceUrl + "/api/v1/algorithms/" + request.getAlgorithmType().toLowerCase();
        return restTemplate.postForObject(url, request, AlgorithmResponse.class);
    }

    private String generateCacheKey(AlgorithmRequest request) {
        String paramsKey = "empty";
        if (request.getParameters() != null && !request.getParameters().isEmpty()) {
            // 使用参数键值对的排序后字符串表示，避免hashCode冲突
            paramsKey = request.getParameters().entrySet().stream()
                    .sorted(Map.Entry.comparingByKey())
                    .map(e -> e.getKey() + "=" + e.getValue())
                    .reduce((a, b) -> a + "&" + b)
                    .orElse("empty");
        }
        return String.format("algorithm:%s:%s", request.getAlgorithmType(), paramsKey);
    }

    private AlgorithmResponse getFromCache(String cacheKey) {
        try {
            return (AlgorithmResponse) redisTemplate.opsForValue().get(cacheKey);
        } catch (Exception e) {
            log.warn("Redis缓存读取失败: {}", e.getMessage());
            return null;
        }
    }

    private void cacheResponse(String cacheKey, AlgorithmResponse response, long ttlSeconds) {
        try {
            redisTemplate.opsForValue().set(cacheKey, response, Duration.ofSeconds(ttlSeconds));
        } catch (Exception e) {
            log.warn("Redis缓存写入失败: {}", e.getMessage());
        }
    }

    private long getCacheTTL(String algorithmType) {
        return switch (algorithmType.toUpperCase()) {
            case "KMEANS", "AHP" -> extendedCacheTtl;
            case "LSTM", "GA" -> mediumCacheTtl;
            default -> standardCacheTtl;
        };
    }
}

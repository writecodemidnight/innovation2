package com.campusclub.service;

import com.campusclub.dto.AlgorithmRequest;
import com.campusclub.dto.AlgorithmResponse;
import com.campusclub.exception.AlgorithmException;
import com.campusclub.exception.AlgorithmTimeoutException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.core.ValueOperations;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeoutException;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;
import static org.junit.jupiter.api.Assertions.*;

@ExtendWith(MockitoExtension.class)
class AlgorithmServiceTest {

    @Mock
    private RestTemplate restTemplate;

    @Mock
    private RedisTemplate<String, Object> redisTemplate;

    @Mock
    private ValueOperations<String, Object> valueOperations;

    @InjectMocks
    private AlgorithmService algorithmService;

    @BeforeEach
    void setUp() {
        // 使用反射设置@Value注解的字段值
        ReflectionTestUtils.setField(algorithmService, "maxRetries", 3);
        ReflectionTestUtils.setField(algorithmService, "algorithmServiceUrl", "http://algorithm-service:8000");
    }

    @Test
    void testExecuteWithRetrySuccess() {
        // Arrange
        AlgorithmResponse mockResponse = AlgorithmResponse.builder()
                .success(true)
                .algorithmType("KMEANS")
                .build();

        when(redisTemplate.opsForValue()).thenReturn(valueOperations);
        when(valueOperations.get(anyString())).thenReturn(null);

        when(restTemplate.postForObject(anyString(), any(), eq(AlgorithmResponse.class)))
                .thenReturn(mockResponse);

        AlgorithmRequest request = AlgorithmRequest.builder()
                .algorithmType("KMEANS")
                .parameters(new HashMap<>())
                .build();

        // Act
        AlgorithmResponse response = algorithmService.executeWithRetry(request);

        // Assert
        assertNotNull(response);
        assertTrue(response.isSuccess());
        assertEquals("KMEANS", response.getAlgorithmType());
    }

    @Test
    void testExecuteWithRetryFromCache() {
        // Arrange
        AlgorithmResponse cachedResponse = AlgorithmResponse.builder()
                .success(true)
                .algorithmType("AHP")
                .build();

        when(redisTemplate.opsForValue()).thenReturn(valueOperations);
        when(valueOperations.get(anyString())).thenReturn(cachedResponse);

        AlgorithmRequest request = AlgorithmRequest.builder()
                .algorithmType("AHP")
                .parameters(Map.of("key", "value"))
                .build();

        // Act
        AlgorithmResponse response = algorithmService.executeWithRetry(request);

        // Assert
        assertNotNull(response);
        assertTrue(response.isSuccess());
        assertEquals("AHP", response.getAlgorithmType());
        verify(restTemplate, never()).postForObject(anyString(), any(), any());
    }

    @Test
    void testExecuteWithRetryTimeout() {
        // Arrange
        when(redisTemplate.opsForValue()).thenReturn(valueOperations);
        when(valueOperations.get(anyString())).thenReturn(null);

        when(restTemplate.postForObject(anyString(), any(), eq(AlgorithmResponse.class)))
                .thenThrow(new RuntimeException(new TimeoutException("Connection timeout")));

        AlgorithmRequest request = AlgorithmRequest.builder()
                .algorithmType("LSTM")
                .parameters(new HashMap<>())
                .build();

        // Act & Assert
        AlgorithmTimeoutException exception = assertThrows(AlgorithmTimeoutException.class,
                () -> algorithmService.executeWithRetry(request));

        assertTrue(exception.getMessage().contains("LSTM"));
        assertTrue(exception.getMessage().contains("超时"));
    }

    @Test
    void testExecuteWithRetryAlgorithmException() {
        // Arrange
        when(redisTemplate.opsForValue()).thenReturn(valueOperations);
        when(valueOperations.get(anyString())).thenReturn(null);

        when(restTemplate.postForObject(anyString(), any(), eq(AlgorithmResponse.class)))
                .thenThrow(new RuntimeException("Service unavailable"));

        AlgorithmRequest request = AlgorithmRequest.builder()
                .algorithmType("GA")
                .parameters(new HashMap<>())
                .build();

        // Act & Assert
        AlgorithmException exception = assertThrows(AlgorithmException.class,
                () -> algorithmService.executeWithRetry(request));

        assertTrue(exception.getMessage().contains("算法执行失败"));
    }

    @Test
    void testExecuteWithRetrySuccessAfterRetry() {
        // Arrange
        AlgorithmResponse mockResponse = AlgorithmResponse.builder()
                .success(true)
                .algorithmType("KMEANS")
                .build();

        when(redisTemplate.opsForValue()).thenReturn(valueOperations);
        when(valueOperations.get(anyString())).thenReturn(null);

        when(restTemplate.postForObject(anyString(), any(), eq(AlgorithmResponse.class)))
                .thenThrow(new RuntimeException(new TimeoutException("First attempt")))
                .thenReturn(mockResponse);

        AlgorithmRequest request = AlgorithmRequest.builder()
                .algorithmType("KMEANS")
                .parameters(new HashMap<>())
                .build();

        // Act
        AlgorithmResponse response = algorithmService.executeWithRetry(request);

        // Assert
        assertNotNull(response);
        assertTrue(response.isSuccess());
        verify(restTemplate, times(2)).postForObject(anyString(), any(), eq(AlgorithmResponse.class));
    }
}

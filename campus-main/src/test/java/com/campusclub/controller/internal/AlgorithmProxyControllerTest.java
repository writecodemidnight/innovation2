package com.campusclub.controller.internal;

import com.campusclub.dto.AlgorithmRequest;
import com.campusclub.dto.AlgorithmResponse;
import com.campusclub.dto.ApiResponse;
import com.campusclub.exception.AlgorithmException;
import com.campusclub.exception.AlgorithmTimeoutException;
import com.campusclub.service.AlgorithmService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import java.util.Map;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;
import static org.junit.jupiter.api.Assertions.*;

@ExtendWith(MockitoExtension.class)
class AlgorithmProxyControllerTest {

    @Mock
    private AlgorithmService algorithmService;

    @InjectMocks
    private AlgorithmProxyController controller;

    @Test
    void testExecuteAlgorithmSuccess() {
        AlgorithmResponse mockResponse = AlgorithmResponse.builder()
                .success(true)
                .algorithmType("KMEANS")
                .result(Map.of("clusters", 3))
                .processingTimeMs(1000L)
                .build();

        when(algorithmService.executeWithRetry(any())).thenReturn(mockResponse);

        AlgorithmRequest request = AlgorithmRequest.builder()
                .algorithmType("KMEANS")
                .parameters(Map.of("clusters", 5))
                .build();

        ResponseEntity<ApiResponse<AlgorithmResponse>> response = controller.executeAlgorithm(request);

        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertNotNull(response.getBody());
        assertTrue(response.getBody().isSuccess());
        verify(algorithmService, times(1)).executeWithRetry(any());
    }

    @Test
    void testExecuteAlgorithmTimeout() {
        when(algorithmService.executeWithRetry(any()))
                .thenThrow(new AlgorithmTimeoutException("Algorithm execution timeout"));

        AlgorithmRequest request = AlgorithmRequest.builder()
                .algorithmType("KMEANS")
                .parameters(Map.of("clusters", 5))
                .build();

        ResponseEntity<ApiResponse<AlgorithmResponse>> response = controller.executeAlgorithm(request);

        assertEquals(HttpStatus.GATEWAY_TIMEOUT, response.getStatusCode());
        assertNotNull(response.getBody());
        assertFalse(response.getBody().isSuccess());
        assertEquals("ALGORITHM_TIMEOUT", response.getBody().getCode());
    }

    @Test
    void testExecuteAlgorithmError() {
        when(algorithmService.executeWithRetry(any()))
                .thenThrow(new AlgorithmException("Algorithm execution failed"));

        AlgorithmRequest request = AlgorithmRequest.builder()
                .algorithmType("KMEANS")
                .parameters(Map.of("clusters", 5))
                .build();

        ResponseEntity<ApiResponse<AlgorithmResponse>> response = controller.executeAlgorithm(request);

        assertEquals(HttpStatus.INTERNAL_SERVER_ERROR, response.getStatusCode());
        assertNotNull(response.getBody());
        assertFalse(response.getBody().isSuccess());
        assertEquals("ALGORITHM_ERROR", response.getBody().getCode());
    }
}

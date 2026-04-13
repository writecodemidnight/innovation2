package com.campusclub.exception;

import com.campusclub.dto.ApiResponse;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.HttpClientErrorException;
import static org.junit.jupiter.api.Assertions.*;

class GlobalExceptionHandlerTest {

    private final GlobalExceptionHandler handler = new GlobalExceptionHandler();

    @Test
    void testHandleAlgorithmTimeout() {
        AlgorithmTimeoutException exception = new AlgorithmTimeoutException("算法超时");
        ResponseEntity<ApiResponse<?>> response = handler.handleAlgorithmTimeout(exception);

        assertEquals(HttpStatus.GATEWAY_TIMEOUT, response.getStatusCode());
        assertNotNull(response.getBody());
        assertEquals("GATEWAY_TIMEOUT", response.getBody().getCode());
        assertTrue(response.getBody().getMessage().contains("算法服务响应超时"));
    }

    @Test
    void testHandleHttpClientError() {
        HttpClientErrorException exception = new HttpClientErrorException(HttpStatus.BAD_GATEWAY, "服务不可用");
        ResponseEntity<ApiResponse<?>> response = handler.handleHttpClientError(exception);

        assertEquals(HttpStatus.BAD_GATEWAY, response.getStatusCode());
        assertNotNull(response.getBody());
        assertEquals("SERVICE_UNAVAILABLE", response.getBody().getCode());
    }
}

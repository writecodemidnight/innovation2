package com.campusclub.exception;

import com.campusclub.dto.ApiResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.client.HttpClientErrorException;

@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    @ExceptionHandler(AlgorithmTimeoutException.class)
    @ResponseStatus(HttpStatus.GATEWAY_TIMEOUT)
    public ResponseEntity<ApiResponse<?>> handleAlgorithmTimeout(AlgorithmTimeoutException e) {
        log.warn("算法服务超时: {}", e.getMessage());
        return ResponseEntity.status(HttpStatus.GATEWAY_TIMEOUT)
                .body(ApiResponse.error("GATEWAY_TIMEOUT",
                    "算法服务响应超时，请稍后重试。如持续出现此问题，请联系管理员。"));
    }

    @ExceptionHandler(HttpClientErrorException.class)
    @ResponseStatus(HttpStatus.BAD_GATEWAY)
    public ResponseEntity<ApiResponse<?>> handleHttpClientError(HttpClientErrorException e) {
        log.error("HTTP客户端错误: {}", e.getMessage());
        return ResponseEntity.status(HttpStatus.BAD_GATEWAY)
                .body(ApiResponse.error("SERVICE_UNAVAILABLE",
                    "依赖服务暂时不可用，请稍后重试。"));
    }

    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ResponseEntity<ApiResponse<?>> handleGenericException(Exception e) {
        log.error("系统异常: ", e);
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(ApiResponse.error("INTERNAL_ERROR",
                    "系统内部错误，请联系管理员。"));
    }
}

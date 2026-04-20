package com.campusclub.controller.internal;

import com.campusclub.dto.AlgorithmRequest;
import com.campusclub.dto.AlgorithmResponse;
import com.campusclub.dto.ApiResponse;
import com.campusclub.exception.AlgorithmException;
import com.campusclub.exception.AlgorithmTimeoutException;
import com.campusclub.service.AlgorithmService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/internal/algorithms")
@Tag(name = "算法服务", description = "内部算法接口，供Java服务调用")
@RequiredArgsConstructor
@Slf4j
public class AlgorithmProxyController {

    private final AlgorithmService algorithmService;

    @PostMapping("/execute")
    @Operation(summary = "执行算法", description = "调用Python算法服务执行计算")
    public ResponseEntity<ApiResponse<AlgorithmResponse>> executeAlgorithm(
            @RequestBody @Valid AlgorithmRequest request) {
        try {
            log.info("执行算法请求: {}", request.getAlgorithmType());
            AlgorithmResponse response = algorithmService.executeWithRetry(request);
            return ResponseEntity.ok(ApiResponse.success(response));
        } catch (AlgorithmTimeoutException e) {
            log.warn("算法执行超时: {}", request.getAlgorithmType(), e);
            return ResponseEntity.status(HttpStatus.GATEWAY_TIMEOUT)
                    .body(ApiResponse.error("ALGORITHM_TIMEOUT",
                        String.format("算法%s执行超时，请稍后重试", request.getAlgorithmType())));
        } catch (AlgorithmException e) {
            log.error("算法执行失败: {}", request.getAlgorithmType(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ApiResponse.error("ALGORITHM_ERROR",
                        String.format("算法%s执行失败: %s", request.getAlgorithmType(), e.getMessage())));
        }
    }
}

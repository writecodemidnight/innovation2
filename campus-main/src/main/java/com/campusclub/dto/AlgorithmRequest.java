package com.campusclub.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Builder;
import lombok.Data;

import java.util.Map;

@Data
@Builder
public class AlgorithmRequest {

    @NotBlank(message = "算法类型不能为空")
    private String algorithmType;

    private Map<String, Object> parameters;

    private Integer timeoutSeconds;
}

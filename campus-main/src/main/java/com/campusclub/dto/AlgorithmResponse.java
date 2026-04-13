package com.campusclub.dto;

import lombok.Builder;
import lombok.Data;

import java.util.Map;

@Data
@Builder
public class AlgorithmResponse {

    private boolean success;

    private String algorithmType;

    private Map<String, Object> result;

    private Long processingTimeMs;

    private String errorMessage;
}

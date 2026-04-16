package com.campusclub.resource.dto;

import lombok.Builder;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@Builder
public class ResourceDTO {
    private Long id;
    private String name;
    private String type;
    private String typeLabel;
    private Integer capacity;
    private String location;
    private String description;
    private BigDecimal hourlyRate;
    private String status;
    private String statusLabel;
    private String facilities;
    private String imageUrl;
    private LocalDateTime createdAt;
}

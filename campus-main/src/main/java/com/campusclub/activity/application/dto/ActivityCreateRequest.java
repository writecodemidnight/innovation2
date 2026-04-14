package com.campusclub.activity.application.dto;

import com.campusclub.activity.domain.entity.Activity;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Future;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public record ActivityCreateRequest(
    @NotBlank @Size(max = 200) String title,
    String description,
    @NotNull Activity.ActivityType activityType,
    @NotNull @Future LocalDateTime startTime,
    @NotNull @Future LocalDateTime endTime,
    @Size(max = 200) String location,
    @Min(1) Integer capacity,
    Long clubId,
    @Size(max = 500) String coverImageUrl,
    @DecimalMin("0.00") BigDecimal budget,
    String requiredResources
) {}

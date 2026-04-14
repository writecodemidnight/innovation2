package com.campusclub.club.application.dto;

import com.campusclub.club.domain.entity.Club;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

public record ClubCreateRequest(
    @NotBlank @Size(max = 100) String name,
    @Size(max = 50) String code,
    String description,
    @NotNull Club.ClubCategory category,
    @Size(max = 500) String logoUrl,
    Long presidentId,
    @Size(max = 100) String facultyAdvisor
) {}

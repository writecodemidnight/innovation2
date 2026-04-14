package com.campusclub.club.application.dto;

import com.campusclub.club.domain.entity.Club;

import java.time.LocalDateTime;

public record ClubDto(
    Long id,
    String name,
    String code,
    String description,
    Club.ClubCategory category,
    String logoUrl,
    Long presidentId,
    String facultyAdvisor,
    Club.ClubStatus status,
    Integer memberCount,
    LocalDateTime createdAt
) {}

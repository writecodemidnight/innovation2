package com.campusclub.club.application.dto;

import com.campusclub.club.domain.entity.ClubMember;

import java.time.LocalDateTime;

public record ClubMemberDto(
    Long id,
    Long clubId,
    Long userId,
    String username,
    String nickname,
    ClubMember.MemberRole role,
    LocalDateTime joinedAt
) {}

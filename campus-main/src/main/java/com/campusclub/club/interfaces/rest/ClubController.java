package com.campusclub.club.interfaces.rest;

import com.campusclub.club.application.dto.*;
import com.campusclub.club.application.service.ClubApplicationService;
import com.campusclub.club.domain.entity.Club;
import com.campusclub.club.domain.entity.ClubMember;
import com.campusclub.dto.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/v1/clubs")
@RequiredArgsConstructor
@Tag(name = "社团", description = "社团管理相关接口")
public class ClubController {

    private final ClubApplicationService clubService;

    @GetMapping
    @Operation(summary = "社团列表", description = "获取社团列表，支持按类别和状态筛选")
    public ResponseEntity<ApiResponse<Page<ClubDto>>> listClubs(
            @RequestParam(required = false) Club.ClubCategory category,
            @RequestParam(required = false) Club.ClubStatus status,
            Pageable pageable) {
        Page<ClubDto> clubs = clubService.listClubs(category, status, pageable);
        return ResponseEntity.ok(ApiResponse.success(clubs));
    }

    @GetMapping("/{id}")
    @Operation(summary = "社团详情", description = "获取社团详细信息")
    public ResponseEntity<ApiResponse<ClubDto>> getClub(@PathVariable Long id) {
        ClubDto club = clubService.getClub(id);
        return ResponseEntity.ok(ApiResponse.success(club));
    }

    @PostMapping
    @PreAuthorize("hasRole('ADMIN') or hasRole('SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "创建社团", description = "创建新社团（管理员权限）")
    public ResponseEntity<ApiResponse<ClubDto>> createClub(
            @RequestBody @Valid ClubCreateRequest request) {
        ClubDto club = clubService.createClub(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(ApiResponse.success(club));
    }

    @PutMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN') or hasRole('SUPER_ADMIN') or @clubSecurity.isClubPresident(#id, authentication)")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "更新社团", description = "更新社团信息")
    public ResponseEntity<ApiResponse<ClubDto>> updateClub(
            @PathVariable Long id,
            @RequestBody @Valid ClubCreateRequest request) {
        ClubDto club = clubService.updateClub(id, request);
        return ResponseEntity.ok(ApiResponse.success(club));
    }

    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN') or hasRole('SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "删除社团", description = "删除社团（管理员权限）")
    public ResponseEntity<ApiResponse<Void>> deleteClub(@PathVariable Long id) {
        clubService.deleteClub(id);
        return ResponseEntity.ok(ApiResponse.success(null));
    }

    @GetMapping("/{id}/members")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "社团成员列表", description = "获取社团成员列表")
    public ResponseEntity<ApiResponse<List<ClubMemberDto>>> listClubMembers(
            @PathVariable Long id) {
        List<ClubMemberDto> members = clubService.listClubMembers(id);
        return ResponseEntity.ok(ApiResponse.success(members));
    }

    @PostMapping("/{id}/members")
    @PreAuthorize("hasRole('ADMIN') or hasRole('SUPER_ADMIN') or @clubSecurity.isClubManager(#id, authentication)")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "添加社团成员", description = "添加成员到社团")
    public ResponseEntity<ApiResponse<Void>> addClubMember(
            @PathVariable Long id,
            @RequestParam Long userId,
            @RequestParam(required = false) ClubMember.MemberRole role) {
        clubService.addClubMember(id, userId, role);
        return ResponseEntity.status(HttpStatus.CREATED).body(ApiResponse.success(null));
    }

    @DeleteMapping("/{id}/members/{userId}")
    @PreAuthorize("hasRole('ADMIN') or hasRole('SUPER_ADMIN') or @clubSecurity.isClubManager(#id, authentication)")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "移除社团成员", description = "从社团移除成员")
    public ResponseEntity<ApiResponse<Void>> removeClubMember(
            @PathVariable Long id,
            @PathVariable Long userId) {
        clubService.removeClubMember(id, userId);
        return ResponseEntity.ok(ApiResponse.success(null));
    }
}

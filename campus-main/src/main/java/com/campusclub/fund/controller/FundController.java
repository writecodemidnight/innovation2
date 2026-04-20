package com.campusclub.fund.controller;

import com.campusclub.common.security.UserContext;
import com.campusclub.dto.ApiResponse;
import com.campusclub.fund.dto.FundApplicationDTO;
import com.campusclub.fund.dto.FundApplyRequest;
import com.campusclub.fund.dto.FundReviewRequest;
import com.campusclub.fund.service.FundApplicationService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

/**
 * 资金管理控制器
 */
@RestController
@RequestMapping("/v1/funds")
@RequiredArgsConstructor
@Tag(name = "资金管理", description = "资金申请和审批相关接口")
public class FundController {

    private final FundApplicationService fundApplicationService;

    /**
     * 提交资金申请
     */
    @PostMapping("/applications")
    @Operation(summary = "提交资金申请", security = @SecurityRequirement(name = "bearerAuth"))
    @PreAuthorize("hasAnyRole('CLUB_PRESIDENT', 'CLUB_MANAGER')")
    public ApiResponse<FundApplicationDTO> apply(
            @Valid @RequestBody FundApplyRequest request) {
        Long clubId = UserContext.getCurrentClubId();
        Long userId = UserContext.getCurrentUserId();
        FundApplicationDTO result = fundApplicationService.apply(request, clubId, userId);
        return ApiResponse.success("申请提交成功", result);
    }

    /**
     * 获取我的资金申请列表
     */
    @GetMapping("/applications/my")
    @Operation(summary = "获取我的资金申请列表", security = @SecurityRequirement(name = "bearerAuth"))
    @PreAuthorize("hasAnyRole('CLUB_PRESIDENT', 'CLUB_MANAGER')")
    public ApiResponse<Page<FundApplicationDTO>> getMyApplications(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        Long userId = UserContext.getCurrentUserId();
        Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());
        Page<FundApplicationDTO> result = fundApplicationService.getUserApplications(userId, pageable);
        return ApiResponse.success(result);
    }

    /**
     * 获取社团的资金申请列表
     */
    @GetMapping("/applications/club")
    @Operation(summary = "获取社团的资金申请列表", security = @SecurityRequirement(name = "bearerAuth"))
    @PreAuthorize("hasAnyRole('CLUB_PRESIDENT', 'CLUB_MANAGER')")
    public ApiResponse<Page<FundApplicationDTO>> getClubApplications(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        Long clubId = UserContext.getCurrentClubId();
        Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());
        Page<FundApplicationDTO> result = fundApplicationService.getClubApplications(clubId, pageable);
        return ApiResponse.success(result);
    }

    /**
     * 获取资金申请详情
     */
    @GetMapping("/applications/{id}")
    @Operation(summary = "获取资金申请详情", security = @SecurityRequirement(name = "bearerAuth"))
    @PreAuthorize("hasAnyRole('CLUB_PRESIDENT', 'CLUB_MANAGER', 'ADMIN')")
    public ApiResponse<FundApplicationDTO> getApplication(@PathVariable Long id) {
        FundApplicationDTO result = fundApplicationService.getApplication(id);
        return ApiResponse.success(result);
    }

    /**
     * 获取所有待审批的申请（管理员）
     */
    @GetMapping("/applications/pending")
    @Operation(summary = "获取所有待审批的申请", security = @SecurityRequirement(name = "bearerAuth"))
    @PreAuthorize("hasRole('ADMIN')")
    public ApiResponse<Page<FundApplicationDTO>> getPendingApplications(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").ascending());
        Page<FundApplicationDTO> result = fundApplicationService.getPendingApplications(pageable);
        return ApiResponse.success(result);
    }

    /**
     * 审批资金申请（通过）
     */
    @PostMapping("/applications/{id}/approve")
    @Operation(summary = "通过资金申请", security = @SecurityRequirement(name = "bearerAuth"))
    @PreAuthorize("hasRole('ADMIN')")
    public ApiResponse<FundApplicationDTO> approve(
            @PathVariable Long id,
            @RequestBody(required = false) FundReviewRequest request) {
        Long reviewerId = UserContext.getCurrentUserId();
        String comment = request != null ? request.getComment() : null;
        FundApplicationDTO result = fundApplicationService.review(id, true, comment, reviewerId);
        return ApiResponse.success("审批通过", result);
    }

    /**
     * 审批资金申请（拒绝）
     */
    @PostMapping("/applications/{id}/reject")
    @Operation(summary = "拒绝资金申请", security = @SecurityRequirement(name = "bearerAuth"))
    @PreAuthorize("hasRole('ADMIN')")
    public ApiResponse<FundApplicationDTO> reject(
            @PathVariable Long id,
            @RequestBody(required = false) FundReviewRequest request) {
        Long reviewerId = UserContext.getCurrentUserId();
        String comment = request != null ? request.getComment() : null;
        FundApplicationDTO result = fundApplicationService.review(id, false, comment, reviewerId);
        return ApiResponse.success("审批已拒绝", result);
    }

    /**
     * 取消资金申请
     */
    @PostMapping("/applications/{id}/cancel")
    @Operation(summary = "取消资金申请", security = @SecurityRequirement(name = "bearerAuth"))
    @PreAuthorize("hasAnyRole('CLUB_PRESIDENT', 'CLUB_MANAGER')")
    public ApiResponse<Void> cancel(
            @PathVariable Long id,
            @RequestParam(required = false) String reason) {
        Long userId = UserContext.getCurrentUserId();
        fundApplicationService.cancel(id, userId, reason);
        return ApiResponse.success("取消成功", null);
    }
}

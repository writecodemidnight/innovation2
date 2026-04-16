package com.campusclub.resource.controller;

import com.campusclub.common.security.UserContext;
import com.campusclub.dto.ApiResponse;
import com.campusclub.resource.domain.entity.Resource;
import com.campusclub.resource.dto.BookingRequestDTO;
import com.campusclub.resource.dto.ResourceBookingDTO;
import com.campusclub.resource.dto.ResourceDTO;
import com.campusclub.resource.service.ResourceService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/v1/resources")
@RequiredArgsConstructor
@Slf4j
public class ResourceController {

    private final ResourceService resourceService;

    /**
     * 获取所有可用资源
     */
    @GetMapping
    public ApiResponse<List<ResourceDTO>> getAvailableResources() {
        List<ResourceDTO> resources = resourceService.getAvailableResources();
        return ApiResponse.success(resources);
    }

    /**
     * 根据类型获取资源
     */
    @GetMapping("/type/{type}")
    public ApiResponse<List<ResourceDTO>> getResourcesByType(
            @PathVariable String type) {
        List<ResourceDTO> resources = resourceService.getResourcesByType(type);
        return ApiResponse.success(resources);
    }

    /**
     * 获取资源详情
     */
    @GetMapping("/{id}")
    public ApiResponse<ResourceDTO> getResourceById(@PathVariable Long id) {
        ResourceDTO resource = resourceService.getResourceById(id);
        if (resource == null) {
            return ApiResponse.error("NOT_FOUND", "资源不存在");
        }
        return ApiResponse.success(resource);
    }

    /**
     * 创建资源预约
     */
    @PostMapping("/bookings")
    @PreAuthorize("hasAnyRole('CLUB_PRESIDENT', 'CLUB_MANAGER')")
    public ApiResponse<ResourceBookingDTO> createBooking(
            @Valid @RequestBody BookingRequestDTO request) {
        try {
            Long clubId = UserContext.getCurrentClubId();
            ResourceBookingDTO booking = resourceService.createBooking(request, clubId);
            return ApiResponse.success("预约申请提交成功", booking);
        } catch (Exception e) {
            log.error("创建预约失败", e);
            return ApiResponse.error("ERROR", e.getMessage());
        }
    }

    /**
     * 获取用户的预约列表
     */
    @GetMapping("/bookings/my")
    @PreAuthorize("hasAnyRole('CLUB_PRESIDENT', 'CLUB_MANAGER')")
    public ApiResponse<List<ResourceBookingDTO>> getMyBookings() {
        Long applicantId = UserContext.getCurrentUserId();
        List<ResourceBookingDTO> bookings = resourceService.getUserBookings(applicantId);
        return ApiResponse.success(bookings);
    }

    /**
     * 取消预约
     */
    @PostMapping("/bookings/{id}/cancel")
    @PreAuthorize("hasAnyRole('CLUB_PRESIDENT', 'CLUB_MANAGER')")
    public ApiResponse<Void> cancelBooking(
            @PathVariable Long id) {
        try {
            Long applicantId = UserContext.getCurrentUserId();
            resourceService.cancelBooking(id, applicantId);
            return ApiResponse.success("取消成功", null);
        } catch (Exception e) {
            log.error("取消预约失败", e);
            return ApiResponse.error("ERROR", e.getMessage());
        }
    }
}

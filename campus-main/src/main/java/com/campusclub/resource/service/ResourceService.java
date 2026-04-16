package com.campusclub.resource.service;

import com.campusclub.activity.domain.repository.ActivityRepository;
import com.campusclub.resource.domain.entity.Resource;
import com.campusclub.resource.domain.entity.ResourceBooking;
import com.campusclub.resource.domain.repository.ResourceBookingRepository;
import com.campusclub.resource.domain.repository.ResourceRepository;
import com.campusclub.resource.dto.BookingRequestDTO;
import com.campusclub.resource.dto.ResourceBookingDTO;
import com.campusclub.resource.dto.ResourceDTO;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class ResourceService {

    private final ResourceRepository resourceRepository;
    private final ResourceBookingRepository bookingRepository;
    private final ActivityRepository activityRepository;

    /**
     * 获取所有可用资源
     */
    public List<ResourceDTO> getAvailableResources() {
        return resourceRepository.findByStatusAndDeletedFalse("AVAILABLE")
                .stream()
                .map(this::convertToResourceDTO)
                .collect(Collectors.toList());
    }

    /**
     * 根据类型获取资源
     */
    public List<ResourceDTO> getResourcesByType(String type) {
        return resourceRepository.findByResourceTypeAndStatusAndDeletedFalse(type, "AVAILABLE")
                .stream()
                .map(this::convertToResourceDTO)
                .collect(Collectors.toList());
    }

    /**
     * 获取资源详情
     */
    public ResourceDTO getResourceById(Long id) {
        return resourceRepository.findById(id)
                .map(this::convertToResourceDTO)
                .orElse(null);
    }

    /**
     * 创建资源预约
     */
    @Transactional
    public ResourceBookingDTO createBooking(BookingRequestDTO request, Long applicantId) {
        // 检查资源是否存在
        Resource resource = resourceRepository.findById(request.getResourceId())
                .orElseThrow(() -> new RuntimeException("资源不存在"));

        // 检查时间冲突
        List<ResourceBooking> conflicts = bookingRepository.findConflictingBookings(
                request.getResourceId(),
                request.getStartTime(),
                request.getEndTime()
        );

        if (!conflicts.isEmpty()) {
            throw new RuntimeException("该时间段资源已被预约");
        }

        // 创建预约
        ResourceBooking booking = ResourceBooking.builder()
                .resourceId(request.getResourceId())
                .activityId(request.getActivityId())
                .applicantId(applicantId)
                .startTime(request.getStartTime())
                .endTime(request.getEndTime())
                .quantity(request.getAttendees() != null ? request.getAttendees() : 1)
                .purpose(request.getRemark())
                .status("PENDING")
                .build();

        ResourceBooking saved = bookingRepository.save(booking);
        return convertToBookingDTO(saved);
    }

    /**
     * 获取用户的预约列表
     */
    public List<ResourceBookingDTO> getUserBookings(Long applicantId) {
        return bookingRepository.findByApplicantIdAndDeletedFalseOrderByCreatedAtDesc(applicantId)
                .stream()
                .map(this::convertToBookingDTO)
                .collect(Collectors.toList());
    }

    /**
     * 获取资源的预约列表
     */
    public List<ResourceBookingDTO> getResourceBookings(Long resourceId) {
        return bookingRepository.findByResourceIdAndDeletedFalse(resourceId)
                .stream()
                .map(this::convertToBookingDTO)
                .collect(Collectors.toList());
    }

    /**
     * 取消预约
     */
    @Transactional
    public void cancelBooking(Long bookingId, Long applicantId) {
        ResourceBooking booking = bookingRepository.findById(bookingId)
                .orElseThrow(() -> new RuntimeException("预约不存在"));

        if (!booking.getApplicantId().equals(applicantId)) {
            throw new RuntimeException("无权取消此预约");
        }

        if ("COMPLETED".equals(booking.getStatus())) {
            throw new RuntimeException("已完成的预约无法取消");
        }

        booking.setStatus("CANCELLED");
        bookingRepository.save(booking);
    }

    private ResourceDTO convertToResourceDTO(Resource resource) {
        return ResourceDTO.builder()
                .id(resource.getId())
                .name(resource.getName())
                .type(resource.getResourceType())
                .typeLabel(getResourceTypeLabel(resource.getResourceType()))
                .capacity(resource.getCapacity())
                .location(resource.getLocation())
                .description(resource.getDescription())
                .status(resource.getStatus())
                .statusLabel(getStatusLabel(resource.getStatus()))
                .build();
    }

    private ResourceBookingDTO convertToBookingDTO(ResourceBooking booking) {
        // 获取关联资源名称
        String resourceName = resourceRepository.findById(booking.getResourceId())
                .map(Resource::getName)
                .orElse("未知资源");

        // 获取关联活动标题
        String activityTitle = activityRepository.findById(booking.getActivityId())
                .map(activity -> activity.getTitle())
                .orElse("活动" + booking.getActivityId());

        return ResourceBookingDTO.builder()
                .id(booking.getId())
                .resourceId(booking.getResourceId())
                .resourceName(resourceName)
                .activityId(booking.getActivityId())
                .activityTitle(activityTitle)
                .startTime(booking.getStartTime())
                .endTime(booking.getEndTime())
                .attendees(booking.getQuantity())
                .status(booking.getStatus())
                .statusLabel(getBookingStatusLabel(booking.getStatus()))
                .remark(booking.getPurpose())
                .createdAt(booking.getCreatedAt())
                .build();
    }

    private String getResourceTypeLabel(String type) {
        return switch (type) {
            case "VENUE" -> "场地";
            case "EQUIPMENT" -> "设备";
            case "VEHICLE" -> "车辆";
            default -> type;
        };
    }

    private String getStatusLabel(String status) {
        return switch (status) {
            case "AVAILABLE" -> "可用";
            case "MAINTENANCE" -> "维护中";
            case "DISABLED" -> "已停用";
            default -> status;
        };
    }

    private String getBookingStatusLabel(String status) {
        return switch (status) {
            case "PENDING" -> "待审核";
            case "APPROVED" -> "已通过";
            case "REJECTED" -> "已拒绝";
            case "CANCELLED" -> "已取消";
            case "COMPLETED" -> "已完成";
            default -> status;
        };
    }
}

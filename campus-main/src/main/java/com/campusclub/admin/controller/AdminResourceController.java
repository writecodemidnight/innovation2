package com.campusclub.admin.controller;

import com.campusclub.common.security.UserContext;
import com.campusclub.dto.ApiResponse;
import com.campusclub.resource.domain.entity.Resource;
import com.campusclub.resource.domain.repository.ResourceRepository;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

/**
 * 管理员资源池管理控制器
 */
@RestController
@RequestMapping("/v1/admin/resources")
@RequiredArgsConstructor
@Tag(name = "管理端资源池", description = "资源池管理接口（增删改查）")
public class AdminResourceController {

    private final ResourceRepository resourceRepository;

    /**
     * 获取资源列表
     */
    @GetMapping
    @PreAuthorize("hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "获取资源列表", description = "分页查询所有资源")
    public ResponseEntity<ApiResponse<Page<Resource>>> listResources(
            @RequestParam(required = false) String resourceType,
            @RequestParam(required = false) String status,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());

        Page<Resource> resources;
        if (resourceType != null && !resourceType.isEmpty()) {
            resources = resourceRepository.findByResourceType(resourceType, pageable);
        } else if (status != null && !status.isEmpty()) {
            resources = resourceRepository.findByStatus(status, pageable);
        } else {
            resources = resourceRepository.findAll(pageable);
        }
        return ResponseEntity.ok(ApiResponse.success(resources));
    }

    /**
     * 获取资源详情
     */
    @GetMapping("/{id}")
    @PreAuthorize("hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "获取资源详情", description = "根据ID获取资源详细信息")
    public ResponseEntity<ApiResponse<Resource>> getResource(@PathVariable Long id) {
        Resource resource = resourceRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("资源不存在"));
        return ResponseEntity.ok(ApiResponse.success(resource));
    }

    /**
     * 创建资源
     */
    @PostMapping
    @PreAuthorize("hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "创建资源", description = "创建新的资源（场地/设备等）")
    public ResponseEntity<ApiResponse<Resource>> createResource(
            @Valid @RequestBody ResourceRequest request) {
        Resource resource = new Resource();
        resource.setName(request.getName());
        resource.setResourceType(request.getResourceType());
        resource.setDescription(request.getDescription());
        resource.setCapacity(request.getCapacity());
        resource.setTotalCount(request.getTotalCount() != null ? request.getTotalCount() : 1);
        resource.setAvailableCount(request.getTotalCount() != null ? request.getTotalCount() : 1);
        resource.setUnit(request.getUnit());
        resource.setLocation(request.getLocation());
        resource.setStatus(request.getStatus() != null ? request.getStatus() : "AVAILABLE");
        resource.setManagerId(UserContext.getCurrentUserId());
        resource.setCreatedAt(LocalDateTime.now());
        resource.setUpdatedAt(LocalDateTime.now());
        resource.setDeleted(false);

        Resource saved = resourceRepository.save(resource);
        return ResponseEntity.ok(ApiResponse.success("资源创建成功", saved));
    }

    /**
     * 更新资源
     */
    @PutMapping("/{id}")
    @PreAuthorize("hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "更新资源", description = "更新资源信息")
    public ResponseEntity<ApiResponse<Resource>> updateResource(
            @PathVariable Long id,
            @Valid @RequestBody ResourceRequest request) {
        Resource resource = resourceRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("资源不存在"));

        resource.setName(request.getName());
        resource.setResourceType(request.getResourceType());
        resource.setDescription(request.getDescription());
        resource.setCapacity(request.getCapacity());
        resource.setUnit(request.getUnit());
        resource.setLocation(request.getLocation());
        if (request.getStatus() != null) {
            resource.setStatus(request.getStatus());
        }
        resource.setUpdatedAt(LocalDateTime.now());

        Resource saved = resourceRepository.save(resource);
        return ResponseEntity.ok(ApiResponse.success("资源更新成功", saved));
    }

    /**
     * 删除资源（逻辑删除）
     */
    @DeleteMapping("/{id}")
    @PreAuthorize("hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "删除资源", description = "逻辑删除资源")
    public ResponseEntity<ApiResponse<Void>> deleteResource(@PathVariable Long id) {
        Resource resource = resourceRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("资源不存在"));
        resource.setDeleted(true);
        resource.setUpdatedAt(LocalDateTime.now());
        resourceRepository.save(resource);
        return ResponseEntity.ok(ApiResponse.success("资源删除成功", null));
    }

    /**
     * 获取资源统计
     */
    @GetMapping("/stats")
    @PreAuthorize("hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "获取资源统计", description = "获取资源池统计信息")
    public ResponseEntity<ApiResponse<Map<String, Object>>> getResourceStats() {
        Map<String, Object> stats = new HashMap<>();

        // 总资源数
        long totalResources = resourceRepository.countByDeletedFalse();
        stats.put("totalResources", totalResources);

        // 各类型资源数
        Map<String, Long> typeStats = new HashMap<>();
        typeStats.put("场地", resourceRepository.countByResourceTypeAndDeletedFalse("VENUE"));
        typeStats.put("设备", resourceRepository.countByResourceTypeAndDeletedFalse("EQUIPMENT"));
        typeStats.put("会议室", resourceRepository.countByResourceTypeAndDeletedFalse("ROOM"));
        stats.put("typeDistribution", typeStats);

        // 可用/不可用统计
        Map<String, Long> statusStats = new HashMap<>();
        statusStats.put("available", resourceRepository.countByStatusAndDeletedFalse("AVAILABLE"));
        statusStats.put("occupied", resourceRepository.countByStatusAndDeletedFalse("OCCUPIED"));
        statusStats.put("maintenance", resourceRepository.countByStatusAndDeletedFalse("MAINTENANCE"));
        stats.put("statusDistribution", statusStats);

        return ResponseEntity.ok(ApiResponse.success(stats));
    }

    /**
     * 资源请求DTO
     */
    public static class ResourceRequest {
        @jakarta.validation.constraints.NotBlank(message = "资源名称不能为空")
        private String name;

        @jakarta.validation.constraints.NotBlank(message = "资源类型不能为空")
        private String resourceType;

        private String description;
        private Integer capacity;
        private Integer totalCount;
        private String unit;
        private String location;
        private String status;

        // Getters and Setters
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public String getResourceType() { return resourceType; }
        public void setResourceType(String resourceType) { this.resourceType = resourceType; }
        public String getDescription() { return description; }
        public void setDescription(String description) { this.description = description; }
        public Integer getCapacity() { return capacity; }
        public void setCapacity(Integer capacity) { this.capacity = capacity; }
        public Integer getTotalCount() { return totalCount; }
        public void setTotalCount(Integer totalCount) { this.totalCount = totalCount; }
        public String getUnit() { return unit; }
        public void setUnit(String unit) { this.unit = unit; }
        public String getLocation() { return location; }
        public void setLocation(String location) { this.location = location; }
        public String getStatus() { return status; }
        public void setStatus(String status) { this.status = status; }
    }
}

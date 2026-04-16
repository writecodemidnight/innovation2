package com.campusclub.resource.domain.entity;

import com.campusclub.common.model.BaseEntity;
import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;

/**
 * 资源实体（场地、设备等）
 */
@Entity
@Table(name = "resources")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Resource extends BaseEntity {

    @Column(nullable = false, length = 100)
    private String name;

    @Column(name = "resource_type", nullable = false, length = 50)
    private String resourceType;

    @Column(length = 500)
    private String description;

    @Column
    private Integer capacity;

    @Column(name = "available_count")
    @Builder.Default
    private Integer availableCount = 0;

    @Column(name = "total_count", nullable = false)
    @Builder.Default
    private Integer totalCount = 1;

    @Column(length = 20)
    private String unit;

    @Column(length = 200)
    private String location;

    @Column(name = "manager_id")
    private Long managerId;

    @Column(columnDefinition = "jsonb")
    private String constraints;

    @Column(length = 20)
    @Builder.Default
    private String status = "AVAILABLE";

    // 兼容字段
    @Transient
    private BigDecimal hourlyRate;

    @Transient
    private String facilities;

    @Transient
    private String imageUrl;
}

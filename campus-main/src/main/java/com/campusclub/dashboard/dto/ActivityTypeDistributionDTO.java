package com.campusclub.dashboard.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * 活动类型分布 DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ActivityTypeDistributionDTO {

    /** 类型分布列表 */
    private List<TypeItem> types;

    /**
     * 单条类型数据
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TypeItem {
        /** 类型名称 */
        private String name;
        /** 类型编码 */
        private String code;
        /** 活动数量 */
        private Integer value;
    }
}

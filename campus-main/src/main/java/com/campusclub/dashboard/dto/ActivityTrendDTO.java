package com.campusclub.dashboard.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * 活动趋势数据 DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ActivityTrendDTO {

    /** 日期列表 */
    private List<String> dates;

    /** 每天的活动数量 */
    private List<Integer> counts;

    /**
     * 单条趋势数据
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TrendItem {
        private String date;
        private Integer count;
    }
}

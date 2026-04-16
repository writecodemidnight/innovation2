package com.campusclub.evaluation.dto;

import lombok.Builder;
import lombok.Data;

import java.util.List;

/**
 * 雷达图数据
 */
@Data
@Builder
public class RadarData {

    private List<String> dimensions;           // 维度名称列表
    private List<Indicator> indicators;        // 雷达图指标配置
    private List<Series> series;               // 数据系列

    @Data
    @Builder
    public static class Indicator {
        private String name;
        private Integer max;
        private String color;
    }

    @Data
    @Builder
    public static class Series {
        private String name;
        private String type;
        private List<Double> value;
        private AreaStyle areaStyle;
        private LineStyle lineStyle;
    }

    @Data
    @Builder
    public static class AreaStyle {
        private Double opacity;
    }

    @Data
    @Builder
    public static class LineStyle {
        private Integer width;
    }
}

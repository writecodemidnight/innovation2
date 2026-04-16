package com.campusclub.resource.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.time.LocalDateTime;

@Data
public class BookingRequestDTO {

    @NotNull(message = "资源ID不能为空")
    private Long resourceId;

    @NotNull(message = "活动ID不能为空")
    private Long activityId;

    @NotNull(message = "开始时间不能为空")
    private LocalDateTime startTime;

    @NotNull(message = "结束时间不能为空")
    private LocalDateTime endTime;

    @NotNull(message = "使用人数不能为空")
    private Integer attendees;

    private String remark;
}

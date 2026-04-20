package com.campusclub.feedback.service;

import com.campusclub.feedback.dto.CreateFeedbackRequest;
import com.campusclub.feedback.dto.FeedbackDTO;
import com.campusclub.feedback.dto.FeedbackStatsDTO;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

/**
 * 反馈评价服务接口
 */
public interface FeedbackService {

    /**
     * 创建反馈评价
     */
    FeedbackDTO createFeedback(CreateFeedbackRequest request, Long userId);

    /**
     * 根据ID获取反馈
     */
    FeedbackDTO getFeedback(Long id);

    /**
     * 获取活动的反馈列表
     */
    Page<FeedbackDTO> getFeedbacksByActivity(Long activityId, Pageable pageable);

    /**
     * 获取用户的反馈列表
     */
    Page<FeedbackDTO> getFeedbacksByUser(Long userId, Pageable pageable);

    /**
     * 获取反馈统计
     */
    FeedbackStatsDTO getFeedbackStats(Long activityId);

    /**
     * 更新反馈
     */
    FeedbackDTO updateFeedback(Long id, CreateFeedbackRequest request, Long userId);

    /**
     * 删除反馈
     */
    void deleteFeedback(Long id, Long userId);

    /**
     * 检查用户是否已评价活动
     */
    boolean hasFeedback(Long activityId, Long userId);
}

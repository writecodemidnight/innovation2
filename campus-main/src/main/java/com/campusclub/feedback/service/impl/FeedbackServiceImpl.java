package com.campusclub.feedback.service.impl;

import com.campusclub.common.exception.BusinessException;
import com.campusclub.feedback.domain.entity.Feedback;
import com.campusclub.feedback.domain.repository.FeedbackRepository;
import com.campusclub.feedback.dto.CreateFeedbackRequest;
import com.campusclub.feedback.dto.FeedbackDTO;
import com.campusclub.feedback.dto.FeedbackStatsDTO;
import com.campusclub.feedback.service.FeedbackService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;

/**
 * 反馈评价服务实现
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class FeedbackServiceImpl implements FeedbackService {

    private final FeedbackRepository feedbackRepository;

    @Override
    @Transactional
    public FeedbackDTO createFeedback(CreateFeedbackRequest request, Long userId) {
        // 检查是否已评价
        if (feedbackRepository.existsByActivityIdAndUserId(request.getActivityId(), userId)) {
            throw new BusinessException("您已对该活动进行过评价", HttpStatus.BAD_REQUEST);
        }

        Feedback feedback = Feedback.builder()
                .activityId(request.getActivityId())
                .userId(userId)
                .rating(request.getRating())
                .content(request.getContent())
                .images(request.getImages())
                .build();

        Feedback saved = feedbackRepository.save(feedback);
        return convertToDTO(saved);
    }

    @Override
    public FeedbackDTO getFeedback(Long id) {
        Feedback feedback = feedbackRepository.findById(id)
                .orElseThrow(() -> new BusinessException("评价不存在", HttpStatus.NOT_FOUND));
        return convertToDTO(feedback);
    }

    @Override
    public Page<FeedbackDTO> getFeedbacksByActivity(Long activityId, Pageable pageable) {
        return feedbackRepository.findByActivityId(activityId, pageable)
                .map(this::convertToDTO);
    }

    @Override
    public Page<FeedbackDTO> getFeedbacksByUser(Long userId, Pageable pageable) {
        return feedbackRepository.findByUserId(userId, pageable)
                .map(this::convertToDTO);
    }

    @Override
    public FeedbackStatsDTO getFeedbackStats(Long activityId) {
        Double averageRating = feedbackRepository.getAverageRating(activityId);
        long totalCount = feedbackRepository.countByActivityId(activityId);
        List<Object[]> distribution = feedbackRepository.getRatingDistribution(activityId);

        // 构建评分分布
        List<FeedbackStatsDTO.RatingDistributionItem> ratingDistribution = new ArrayList<>();
        for (int i = 5; i >= 1; i--) {
            final int stars = i;
            long count = distribution.stream()
                    .filter(arr -> stars == (Integer) arr[0])
                    .mapToLong(arr -> (Long) arr[1])
                    .sum();
            double percentage = totalCount > 0 ? (count * 100.0 / totalCount) : 0;
            ratingDistribution.add(FeedbackStatsDTO.RatingDistributionItem.builder()
                    .stars(stars)
                    .count(count)
                    .percentage(Math.round(percentage * 100.0) / 100.0)
                    .build());
        }

        return FeedbackStatsDTO.builder()
                .activityId(activityId)
                .averageRating(averageRating != null ? Math.round(averageRating * 100.0) / 100.0 : 0.0)
                .totalCount(totalCount)
                .ratingDistribution(ratingDistribution)
                .build();
    }

    @Override
    @Transactional
    public FeedbackDTO updateFeedback(Long id, CreateFeedbackRequest request, Long userId) {
        Feedback feedback = feedbackRepository.findById(id)
                .orElseThrow(() -> new BusinessException("评价不存在", HttpStatus.NOT_FOUND));

        if (!feedback.getUserId().equals(userId)) {
            throw new BusinessException("无权修改他人评价", HttpStatus.FORBIDDEN);
        }

        feedback.setRating(request.getRating());
        feedback.setContent(request.getContent());
        feedback.setImages(request.getImages());

        Feedback updated = feedbackRepository.save(feedback);
        return convertToDTO(updated);
    }

    @Override
    @Transactional
    public void deleteFeedback(Long id, Long userId) {
        Feedback feedback = feedbackRepository.findById(id)
                .orElseThrow(() -> new BusinessException("评价不存在", HttpStatus.NOT_FOUND));

        if (!feedback.getUserId().equals(userId)) {
            throw new BusinessException("无权删除他人评价", HttpStatus.FORBIDDEN);
        }

        feedbackRepository.delete(feedback);
    }

    @Override
    public boolean hasFeedback(Long activityId, Long userId) {
        return feedbackRepository.existsByActivityIdAndUserId(activityId, userId);
    }

    /**
     * 转换为DTO
     */
    private FeedbackDTO convertToDTO(Feedback feedback) {
        return FeedbackDTO.builder()
                .id(feedback.getId())
                .activityId(feedback.getActivityId())
                .userId(feedback.getUserId())
                .rating(feedback.getRating())
                .content(feedback.getContent())
                .images(feedback.getImages())
                .createdAt(feedback.getCreatedAt())
                .updatedAt(feedback.getUpdatedAt())
                .build();
    }
}

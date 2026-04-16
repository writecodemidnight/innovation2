package com.campusclub.fund.service.impl;

import com.campusclub.activity.domain.entity.Activity;
import com.campusclub.activity.domain.repository.ActivityRepository;
import com.campusclub.club.domain.entity.Club;
import com.campusclub.club.domain.repository.ClubRepository;
import com.campusclub.common.exception.BusinessException;
import com.campusclub.common.exception.NotFoundException;
import com.campusclub.fund.domain.entity.FundApplication;
import com.campusclub.fund.dto.FundApplicationDTO;
import com.campusclub.fund.dto.FundApplyRequest;
import com.campusclub.fund.repository.FundApplicationRepository;
import com.campusclub.fund.service.FundApplicationService;
import com.campusclub.user.domain.entity.User;
import com.campusclub.user.domain.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

/**
 * 资金申请服务实现类
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class FundApplicationServiceImpl implements FundApplicationService {

    private final FundApplicationRepository fundApplicationRepository;
    private final ClubRepository clubRepository;
    private final UserRepository userRepository;
    private final ActivityRepository activityRepository;

    @Override
    @Transactional
    public FundApplicationDTO apply(FundApplyRequest request, Long clubId, Long userId) {
        // 验证社团存在
        Club club = clubRepository.findById(clubId)
                .orElseThrow(() -> new NotFoundException("社团不存在: " + clubId));

        // 验证用户存在
        User applicant = userRepository.findById(userId)
                .orElseThrow(() -> new NotFoundException("用户不存在: " + userId));

        // 验证活动存在
        Activity activity = activityRepository.findById(request.getActivityId())
                .orElseThrow(() -> new NotFoundException("活动不存在: " + request.getActivityId()));

        // 检查是否已申请过该活动的资金
        List<FundApplication> existingApplications = fundApplicationRepository.findByActivityId(request.getActivityId());
        boolean hasPendingOrApproved = existingApplications.stream()
                .anyMatch(app -> app.getStatus() == FundApplication.FundStatus.PENDING
                        || app.getStatus() == FundApplication.FundStatus.APPROVED);

        if (hasPendingOrApproved) {
            throw new BusinessException("该活动已有待审批或已批准的资金申请");
        }

        // 创建申请
        FundApplication application = FundApplication.builder()
                .club(club)
                .activity(activity)
                .applicant(applicant)
                .amount(request.getAmount())
                .purpose(request.getPurpose())
                .budgetBreakdown(request.getBudgetBreakdown())
                .status(FundApplication.FundStatus.PENDING)
                .build();

        FundApplication saved = fundApplicationRepository.save(application);
        log.info("资金申请提交成功: id={}, clubId={}, amount={}", saved.getId(), clubId, request.getAmount());

        return toDTO(saved);
    }

    @Override
    @Transactional(readOnly = true)
    public FundApplicationDTO getApplication(Long id) {
        FundApplication application = fundApplicationRepository.findById(id)
                .orElseThrow(() -> new NotFoundException("资金申请不存在: " + id));
        return toDTO(application);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<FundApplicationDTO> getClubApplications(Long clubId, Pageable pageable) {
        Page<FundApplication> applications = fundApplicationRepository.findByClubIdOrderByCreatedAtDesc(clubId, pageable);
        return applications.map(this::toDTO);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<FundApplicationDTO> getUserApplications(Long userId, Pageable pageable) {
        Page<FundApplication> applications = fundApplicationRepository.findByApplicantIdOrderByCreatedAtDesc(userId, pageable);
        return applications.map(this::toDTO);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<FundApplicationDTO> getPendingApplications(Pageable pageable) {
        Page<FundApplication> applications = fundApplicationRepository.findByStatusOrderByCreatedAtDesc(
                FundApplication.FundStatus.PENDING, pageable);
        return applications.map(this::toDTO);
    }

    @Override
    @Transactional
    public FundApplicationDTO review(Long id, boolean approved, String comment, Long reviewerId) {
        FundApplication application = fundApplicationRepository.findById(id)
                .orElseThrow(() -> new NotFoundException("资金申请不存在: " + id));

        if (!application.canReview()) {
            throw new BusinessException("该申请当前状态不可审批");
        }

        User reviewer = userRepository.findById(reviewerId)
                .orElseThrow(() -> new NotFoundException("审批人不存在: " + reviewerId));

        if (approved) {
            application.approve(reviewer, comment);
            log.info("资金申请审批通过: id={}, reviewerId={}", id, reviewerId);
        } else {
            application.reject(reviewer, comment);
            log.info("资金申请审批拒绝: id={}, reviewerId={}", id, reviewerId);
        }

        FundApplication saved = fundApplicationRepository.save(application);
        return toDTO(saved);
    }

    @Override
    @Transactional
    public void cancel(Long id, Long userId, String reason) {
        FundApplication application = fundApplicationRepository.findById(id)
                .orElseThrow(() -> new NotFoundException("资金申请不存在: " + id));

        // 验证是否是申请人本人
        if (!application.getApplicant().getId().equals(userId)) {
            throw new BusinessException("只能取消自己的申请");
        }

        if (!application.canCancel()) {
            throw new BusinessException("该申请当前状态不可取消");
        }

        application.cancel(reason);
        fundApplicationRepository.save(application);
        log.info("资金申请取消成功: id={}, userId={}", id, userId);
    }

    @Override
    public FundApplicationDTO toDTO(FundApplication application) {
        if (application == null) return null;

        return FundApplicationDTO.builder()
                .id(application.getId())
                .clubId(application.getClub() != null ? application.getClub().getId() : null)
                .clubName(application.getClub() != null ? application.getClub().getName() : null)
                .activityId(application.getActivity() != null ? application.getActivity().getId() : null)
                .activityTitle(application.getActivity() != null ? application.getActivity().getTitle() : null)
                .applicantId(application.getApplicant() != null ? application.getApplicant().getId() : null)
                .applicantName(application.getApplicant() != null ? application.getApplicant().getUsername() : null)
                .amount(application.getAmount())
                .purpose(application.getPurpose())
                .budgetBreakdown(application.getBudgetBreakdown())
                .status(application.getStatus())
                .reviewerId(application.getReviewer() != null ? application.getReviewer().getId() : null)
                .reviewerName(application.getReviewer() != null ? application.getReviewer().getUsername() : null)
                .reviewerComment(application.getReviewerComment())
                .reviewedAt(application.getReviewedAt())
                .cancelledAt(application.getCancelledAt())
                .cancelReason(application.getCancelReason())
                .createdAt(application.getCreatedAt())
                .build();
    }
}

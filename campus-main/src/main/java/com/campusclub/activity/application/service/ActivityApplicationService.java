package com.campusclub.activity.application.service;

import com.campusclub.activity.application.dto.ActivityCreateRequest;
import com.campusclub.activity.application.dto.ActivityDto;
import com.campusclub.activity.application.dto.ActivityParticipantDto;
import com.campusclub.activity.application.mapper.ActivityMapper;
import com.campusclub.activity.domain.entity.Activity;
import com.campusclub.activity.domain.entity.ActivityParticipant;
import com.campusclub.activity.domain.repository.ActivityParticipantRepository;
import com.campusclub.activity.domain.repository.ActivityRepository;
import com.campusclub.club.domain.entity.Club;
import com.campusclub.club.domain.repository.ClubRepository;
import com.campusclub.common.exception.BusinessException;
import com.campusclub.common.security.UserContext;
import com.campusclub.user.domain.entity.User;
import com.campusclub.user.domain.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ActivityApplicationService {

    private static final String ERR_ACTIVITY_NOT_FOUND = "Activity not found with id: %d";
    private static final String ERR_USER_NOT_FOUND = "User not found with id: %d";
    private static final String ERR_CLUB_NOT_FOUND = "Club not found with id: %d";
    private static final String ERR_REGISTRATION_NOT_FOUND = "Registration not found for this activity";
    private static final String ERR_ALREADY_REGISTERED = "User already registered for this activity";
    private static final String ERR_ONLY_PLANNING_EDITABLE = "Only PLANNING activities can be edited. Current status: %s";
    private static final String ERR_ONLY_PLANNING_DELETABLE = "Only PLANNING activities can be deleted. Current status: %s";
    private static final String ERR_ONLY_REGISTERED_CAN_CANCEL = "Only REGISTERED participants can cancel. Current status: %s";
    private static final String ERR_CANNOT_REGISTER = "Cannot register for this activity. Status: %s, Capacity: %s, Current: %s";

    private final ActivityRepository activityRepository;
    private final ActivityParticipantRepository participantRepository;
    private final ClubRepository clubRepository;
    private final UserRepository userRepository;
    private final ActivityMapper activityMapper;

    @Transactional(readOnly = true)
    public Page<ActivityDto> listActivities(
            Activity.ActivityStatus status,
            Activity.ActivityType type,
            Long clubId,
            Pageable pageable) {
        Page<Activity> activities;

        if (clubId != null && status != null) {
            // 社团内部查看指定状态的活动
            activities = activityRepository.findByClubIdAndStatus(clubId, status, pageable);
        } else if (clubId != null) {
            // 查看指定社团的所有活动（社团端需要看到所有状态的活动）
            activities = activityRepository.findByClubId(clubId, pageable);
        } else if (status != null) {
            // 按状态筛选
            activities = activityRepository.findByStatus(status, pageable);
        } else if (type != null) {
            // 按类型筛选公开活动
            activities = activityRepository.findPublicActivitiesByType(type, pageable);
        } else {
            // 默认只返回已批准的公开活动
            activities = activityRepository.findPublicActivities(pageable);
        }

        return enrichWithClubName(activities);
    }

    @Transactional(readOnly = true)
    public ActivityDto getActivity(Long id) {
        Activity activity = findActivityById(id);
        ActivityDto dto = activityMapper.toDto(activity);
        return enrichWithClubName(dto);
    }

    @Transactional
    public ActivityDto createActivity(Long userId, ActivityCreateRequest request) {
        validateUserExists(userId);

        // 如果没有指定clubId，自动使用当前用户的社团（目前只有一个社团id=5）
        Long clubId = request.clubId();
        if (clubId == null) {
            clubId = UserContext.getCurrentClubId();
        }

        // 验证社团存在
        validateClubExists(clubId);

        Activity activity = activityMapper.toEntity(request);
        activity.setCreatedBy(userId);
        activity.setClubId(clubId);
        activity.setStatus(Activity.ActivityStatus.PENDING_APPROVAL);
        activity.setApprovalStatus(Activity.ApprovalStatus.NONE);
        activity.setCurrentParticipants(0);

        Activity savedActivity = activityRepository.save(activity);
        return enrichWithClubName(activityMapper.toDto(savedActivity));
    }

    @Transactional
    public ActivityDto updateActivity(Long id, ActivityCreateRequest request) {
        Activity activity = findActivityById(id);

        if (activity.getStatus() != Activity.ActivityStatus.PLANNING) {
            throw new BusinessException(String.format(ERR_ONLY_PLANNING_EDITABLE, activity.getStatus()),
                    HttpStatus.BAD_REQUEST);
        }

        if (request.clubId() != null) {
            validateClubExists(request.clubId());
        }

        activity.setTitle(request.title());
        activity.setDescription(request.description());
        activity.setActivityType(request.activityType());
        activity.setStartTime(request.startTime());
        activity.setEndTime(request.endTime());
        activity.setLocation(request.location());
        activity.setCapacity(request.capacity());
        activity.setClubId(request.clubId());
        activity.setCoverImageUrl(request.coverImageUrl());
        activity.setBudget(request.budget());
        activity.setRequiredResources(request.requiredResources());
        activity.setRegistrationDeadline(request.registrationDeadline());

        Activity updatedActivity = activityRepository.save(activity);
        return enrichWithClubName(activityMapper.toDto(updatedActivity));
    }

    @Transactional
    public void deleteActivity(Long id) {
        Activity activity = findActivityById(id);

        if (activity.getStatus() != Activity.ActivityStatus.PLANNING) {
            throw new BusinessException(String.format(ERR_ONLY_PLANNING_DELETABLE, activity.getStatus()),
                    HttpStatus.BAD_REQUEST);
        }

        activity.setDeleted(true);
        activityRepository.save(activity);
    }

    @Transactional
    public void submitForApproval(Long id) {
        Activity activity = findActivityById(id);
        activity.submitForApproval();
        activityRepository.save(activity);
    }

    @Transactional
    public void registerForActivity(Long activityId, Long userId) {
        Activity activity = findActivityById(activityId);
        validateUserExists(userId);

        if (!activity.canRegister()) {
            throw new BusinessException(String.format(ERR_CANNOT_REGISTER,
                    activity.getStatus(), activity.getCapacity(), activity.getCurrentParticipants()),
                    HttpStatus.BAD_REQUEST);
        }

        if (participantRepository.existsByActivityIdAndUserId(activityId, userId)) {
            throw new BusinessException(ERR_ALREADY_REGISTERED, HttpStatus.BAD_REQUEST);
        }

        ActivityParticipant participant = ActivityParticipant.builder()
                .activityId(activityId)
                .userId(userId)
                .status(ActivityParticipant.ParticipationStatus.REGISTERED)
                .registeredAt(LocalDateTime.now())
                .build();

        participantRepository.save(participant);

        int updated = activityRepository.incrementParticipants(activityId);
        if (updated == 0) {
            throw new BusinessException("Activity capacity reached", HttpStatus.BAD_REQUEST);
        }
    }

    @Transactional
    public void cancelRegistration(Long activityId, Long userId) {
        Activity activity = findActivityById(activityId);
        ActivityParticipant participant = participantRepository.findByActivityIdAndUserId(activityId, userId)
                .orElseThrow(() -> new BusinessException(ERR_REGISTRATION_NOT_FOUND, HttpStatus.NOT_FOUND));

        if (participant.getStatus() != ActivityParticipant.ParticipationStatus.REGISTERED) {
            throw new BusinessException(String.format(ERR_ONLY_REGISTERED_CAN_CANCEL, participant.getStatus()),
                    HttpStatus.BAD_REQUEST);
        }

        participant.cancel();
        participantRepository.save(participant);

        activityRepository.decrementParticipants(activityId);
    }

    @Transactional
    public void checkIn(Long activityId, Long userId) {
        findActivityById(activityId);
        ActivityParticipant participant = participantRepository.findByActivityIdAndUserId(activityId, userId)
                .orElseThrow(() -> new BusinessException(ERR_REGISTRATION_NOT_FOUND, HttpStatus.NOT_FOUND));

        participant.checkIn();
        participantRepository.save(participant);
    }

    @Transactional(readOnly = true)
    public List<ActivityParticipantDto> listParticipants(Long activityId) {
        findActivityById(activityId);
        List<ActivityParticipant> participants = participantRepository.findByActivityId(activityId);

        Map<Long, User> userMap = userRepository.findAllById(
                participants.stream().map(ActivityParticipant::getUserId).toList()
        ).stream().collect(Collectors.toMap(User::getId, Function.identity()));

        return participants.stream()
                .map(p -> activityMapper.toParticipantDto(p, userMap.get(p.getUserId())))
                .toList();
    }

    @Transactional(readOnly = true)
    public List<ActivityDto> listMyActivities(Long userId) {
        validateUserExists(userId);
        List<ActivityParticipant> registrations = participantRepository.findByUserId(userId);

        List<Long> activityIds = registrations.stream()
                .map(ActivityParticipant::getActivityId)
                .toList();

        List<Activity> activities = activityRepository.findAllById(activityIds);
        return enrichWithClubName(activities);
    }

    private Activity findActivityById(Long id) {
        return activityRepository.findById(id)
                .orElseThrow(() -> new BusinessException(String.format(ERR_ACTIVITY_NOT_FOUND, id), HttpStatus.NOT_FOUND));
    }

    private void validateUserExists(Long userId) {
        if (!userRepository.existsById(userId)) {
            throw new BusinessException(String.format(ERR_USER_NOT_FOUND, userId), HttpStatus.NOT_FOUND);
        }
    }

    private void validateClubExists(Long clubId) {
        if (!clubRepository.existsById(clubId)) {
            throw new BusinessException(String.format(ERR_CLUB_NOT_FOUND, clubId), HttpStatus.NOT_FOUND);
        }
    }

    private Page<ActivityDto> enrichWithClubName(Page<Activity> activities) {
        Map<Long, String> clubNameMap = getClubNameMap(
                activities.getContent().stream().map(Activity::getClubId).filter(id -> id != null).toList()
        );
        return activities.map(activity -> enrichDtoWithClubName(activityMapper.toDto(activity), clubNameMap));
    }

    private ActivityDto enrichWithClubName(ActivityDto dto) {
        if (dto.clubId() == null) {
            return dto;
        }
        String clubName = clubRepository.findById(dto.clubId())
                .map(Club::getName)
                .orElse(null);
        return copyWithClubName(dto, clubName);
    }

    private List<ActivityDto> enrichWithClubName(List<Activity> activities) {
        Map<Long, String> clubNameMap = getClubNameMap(
                activities.stream().map(Activity::getClubId).filter(id -> id != null).toList()
        );
        return activities.stream()
                .map(activity -> enrichDtoWithClubName(activityMapper.toDto(activity), clubNameMap))
                .toList();
    }

    private Map<Long, String> getClubNameMap(List<Long> clubIds) {
        if (clubIds.isEmpty()) {
            return Map.of();
        }
        return clubRepository.findAllById(clubIds).stream()
                .collect(Collectors.toMap(Club::getId, Club::getName));
    }

    private ActivityDto enrichDtoWithClubName(ActivityDto dto, Map<Long, String> clubNameMap) {
        return copyWithClubName(dto, clubNameMap.getOrDefault(dto.clubId(), null));
    }

    private ActivityDto copyWithClubName(ActivityDto dto, String clubName) {
        return new ActivityDto(
                dto.id(),
                dto.title(),
                dto.description(),
                dto.activityType(),
                dto.status(),
                dto.startTime(),
                dto.endTime(),
                dto.location(),
                dto.capacity(),
                dto.currentParticipants(),
                dto.clubId(),
                clubName,
                dto.createdBy(),
                dto.coverImageUrl(),
                dto.budget(),
                dto.approvalStatus(),
                dto.registrationDeadline(),
                dto.createdAt()
        );
    }

    // ========== Recommendation Methods ==========

    @Transactional(readOnly = true)
    public List<ActivityDto> getHotActivities() {
        List<Activity> activities = activityRepository.findHotActivities(Pageable.ofSize(10));
        return enrichWithClubName(activities);
    }

    @Transactional(readOnly = true)
    public List<ActivityDto> getUpcomingActivities() {
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime endTime = now.plusDays(7);
        List<Activity> activities = activityRepository.findUpcomingActivities(now, endTime, Pageable.ofSize(10));
        return enrichWithClubName(activities);
    }

    @Transactional(readOnly = true)
    public List<ActivityDto> getRecommendedActivities(Long userId) {
        // 简化版推荐：基于用户历史参与类型进行推荐
        // 实际生产环境应该调用推荐算法服务
        Activity.ActivityType preferredType = null;
        if (userId != null) {
            preferredType = getUserPreferredActivityType(userId);
        }
        List<Activity> activities = activityRepository.findRecommendedActivities(preferredType, Pageable.ofSize(10));
        return enrichWithClubName(activities);
    }

    private Activity.ActivityType getUserPreferredActivityType(Long userId) {
        // 获取用户最常参与的活动类型
        List<ActivityParticipant> participations = participantRepository.findByUserId(userId);
        if (participations.isEmpty()) {
            return null;
        }

        List<Long> activityIds = participations.stream()
                .map(ActivityParticipant::getActivityId)
                .toList();

        List<Activity> activities = activityRepository.findAllById(activityIds);
        return activities.stream()
                .collect(Collectors.groupingBy(Activity::getActivityType, Collectors.counting()))
                .entrySet().stream()
                .max(Map.Entry.comparingByValue())
                .map(Map.Entry::getKey)
                .orElse(null);
    }
}

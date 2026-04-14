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
    private static final String ERR_ONLY_DRAFT_EDITABLE = "Only DRAFT activities can be edited. Current status: %s";
    private static final String ERR_ONLY_DRAFT_DELETABLE = "Only DRAFT activities can be deleted. Current status: %s";
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
            activities = activityRepository.findByClubIdAndStatus(clubId, status, pageable);
        } else if (clubId != null) {
            activities = activityRepository.findByClubId(clubId, pageable);
        } else if (status != null) {
            activities = activityRepository.findByStatus(status, pageable);
        } else if (type != null) {
            activities = activityRepository.findByActivityType(type, pageable);
        } else {
            activities = activityRepository.findAll(pageable);
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
        if (request.clubId() != null) {
            validateClubExists(request.clubId());
        }

        Activity activity = activityMapper.toEntity(request);
        activity.setCreatedBy(userId);
        activity.setStatus(Activity.ActivityStatus.DRAFT);
        activity.setApprovalStatus(Activity.ApprovalStatus.NONE);
        activity.setCurrentParticipants(0);

        Activity savedActivity = activityRepository.save(activity);
        return enrichWithClubName(activityMapper.toDto(savedActivity));
    }

    @Transactional
    public ActivityDto updateActivity(Long id, ActivityCreateRequest request) {
        Activity activity = findActivityById(id);

        if (activity.getStatus() != Activity.ActivityStatus.DRAFT) {
            throw new BusinessException(String.format(ERR_ONLY_DRAFT_EDITABLE, activity.getStatus()),
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

        Activity updatedActivity = activityRepository.save(activity);
        return enrichWithClubName(activityMapper.toDto(updatedActivity));
    }

    @Transactional
    public void deleteActivity(Long id) {
        Activity activity = findActivityById(id);

        if (activity.getStatus() != Activity.ActivityStatus.DRAFT) {
            throw new BusinessException(String.format(ERR_ONLY_DRAFT_DELETABLE, activity.getStatus()),
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
                dto.createdAt()
        );
    }
}

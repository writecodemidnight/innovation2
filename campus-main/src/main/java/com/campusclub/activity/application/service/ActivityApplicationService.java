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
        Activity activity = activityRepository.findById(id)
                .orElseThrow(() -> new BusinessException("Activity not found with id: " + id, HttpStatus.NOT_FOUND));
        ActivityDto dto = activityMapper.toDto(activity);
        return enrichWithClubName(dto);
    }

    @Transactional
    public ActivityDto createActivity(Long userId, ActivityCreateRequest request) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException("User not found with id: " + userId, HttpStatus.NOT_FOUND));

        if (request.clubId() != null) {
            Club club = clubRepository.findById(request.clubId())
                    .orElseThrow(() -> new BusinessException("Club not found with id: " + request.clubId(), HttpStatus.NOT_FOUND));
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
        Activity activity = activityRepository.findById(id)
                .orElseThrow(() -> new BusinessException("Activity not found with id: " + id, HttpStatus.NOT_FOUND));

        if (activity.getStatus() != Activity.ActivityStatus.DRAFT) {
            throw new BusinessException("Only DRAFT activities can be edited. Current status: " + activity.getStatus(),
                    HttpStatus.BAD_REQUEST);
        }

        if (request.clubId() != null) {
            Club club = clubRepository.findById(request.clubId())
                    .orElseThrow(() -> new BusinessException("Club not found with id: " + request.clubId(), HttpStatus.NOT_FOUND));
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
        Activity activity = activityRepository.findById(id)
                .orElseThrow(() -> new BusinessException("Activity not found with id: " + id, HttpStatus.NOT_FOUND));

        if (activity.getStatus() != Activity.ActivityStatus.DRAFT) {
            throw new BusinessException("Only DRAFT activities can be deleted. Current status: " + activity.getStatus(),
                    HttpStatus.BAD_REQUEST);
        }

        activityRepository.delete(activity);
    }

    @Transactional
    public void submitForApproval(Long id) {
        Activity activity = activityRepository.findById(id)
                .orElseThrow(() -> new BusinessException("Activity not found with id: " + id, HttpStatus.NOT_FOUND));

        activity.submitForApproval();
        activityRepository.save(activity);
    }

    @Transactional
    public void registerForActivity(Long activityId, Long userId) {
        Activity activity = activityRepository.findById(activityId)
                .orElseThrow(() -> new BusinessException("Activity not found with id: " + activityId, HttpStatus.NOT_FOUND));

        User user = userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException("User not found with id: " + userId, HttpStatus.NOT_FOUND));

        if (!activity.canRegister()) {
            throw new BusinessException("Cannot register for this activity. Status: " + activity.getStatus() +
                    ", Capacity: " + activity.getCapacity() + ", Current: " + activity.getCurrentParticipants(),
                    HttpStatus.BAD_REQUEST);
        }

        if (participantRepository.existsByActivityIdAndUserId(activityId, userId)) {
            throw new BusinessException("User already registered for this activity", HttpStatus.BAD_REQUEST);
        }

        ActivityParticipant participant = ActivityParticipant.builder()
                .activityId(activityId)
                .userId(userId)
                .status(ActivityParticipant.ParticipationStatus.REGISTERED)
                .registeredAt(LocalDateTime.now())
                .build();

        participantRepository.save(participant);

        activity.setCurrentParticipants(activity.getCurrentParticipants() + 1);
        activityRepository.save(activity);
    }

    @Transactional
    public void cancelRegistration(Long activityId, Long userId) {
        Activity activity = activityRepository.findById(activityId)
                .orElseThrow(() -> new BusinessException("Activity not found with id: " + activityId, HttpStatus.NOT_FOUND));

        ActivityParticipant participant = participantRepository.findByActivityIdAndUserId(activityId, userId)
                .orElseThrow(() -> new BusinessException("Registration not found for this activity", HttpStatus.NOT_FOUND));

        if (participant.getStatus() != ActivityParticipant.ParticipationStatus.REGISTERED) {
            throw new BusinessException("Only REGISTERED participants can cancel. Current status: " + participant.getStatus(),
                    HttpStatus.BAD_REQUEST);
        }

        participant.cancel();
        participantRepository.save(participant);

        activity.setCurrentParticipants(Math.max(0, activity.getCurrentParticipants() - 1));
        activityRepository.save(activity);
    }

    @Transactional
    public void checkIn(Long activityId, Long userId) {
        Activity activity = activityRepository.findById(activityId)
                .orElseThrow(() -> new BusinessException("Activity not found with id: " + activityId, HttpStatus.NOT_FOUND));

        ActivityParticipant participant = participantRepository.findByActivityIdAndUserId(activityId, userId)
                .orElseThrow(() -> new BusinessException("Registration not found for this activity", HttpStatus.NOT_FOUND));

        participant.checkIn();
        participantRepository.save(participant);
    }

    @Transactional(readOnly = true)
    public List<ActivityParticipantDto> listParticipants(Long activityId) {
        Activity activity = activityRepository.findById(activityId)
                .orElseThrow(() -> new BusinessException("Activity not found with id: " + activityId, HttpStatus.NOT_FOUND));

        List<ActivityParticipant> participants = participantRepository.findByActivityId(activityId);

        Set<Long> userIds = participants.stream()
                .map(ActivityParticipant::getUserId)
                .collect(Collectors.toSet());

        Map<Long, User> userMap = userRepository.findAllById(userIds).stream()
                .collect(Collectors.toMap(User::getId, Function.identity()));

        return participants.stream()
                .map(p -> activityMapper.toParticipantDto(p, userMap.get(p.getUserId())))
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<ActivityDto> listMyActivities(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException("User not found with id: " + userId, HttpStatus.NOT_FOUND));

        List<ActivityParticipant> registrations = participantRepository.findByUserId(userId);

        Set<Long> activityIds = registrations.stream()
                .map(ActivityParticipant::getActivityId)
                .collect(Collectors.toSet());

        List<Activity> activities = activityRepository.findAllById(activityIds);

        return enrichWithClubName(activities);
    }

    private Page<ActivityDto> enrichWithClubName(Page<Activity> activities) {
        Set<Long> clubIds = activities.getContent().stream()
                .map(Activity::getClubId)
                .filter(id -> id != null)
                .collect(Collectors.toSet());

        Map<Long, String> clubNameMap = clubRepository.findAllById(clubIds).stream()
                .collect(Collectors.toMap(Club::getId, Club::getName));

        return activities.map(activity -> {
            ActivityDto dto = activityMapper.toDto(activity);
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
                    clubNameMap.getOrDefault(dto.clubId(), null),
                    dto.createdBy(),
                    dto.coverImageUrl(),
                    dto.budget(),
                    dto.approvalStatus(),
                    dto.createdAt()
            );
        });
    }

    private ActivityDto enrichWithClubName(ActivityDto dto) {
        if (dto.clubId() == null) {
            return dto;
        }
        String clubName = clubRepository.findById(dto.clubId())
                .map(Club::getName)
                .orElse(null);
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

    private List<ActivityDto> enrichWithClubName(List<Activity> activities) {
        Set<Long> clubIds = activities.stream()
                .map(Activity::getClubId)
                .filter(id -> id != null)
                .collect(Collectors.toSet());

        Map<Long, String> clubNameMap = clubRepository.findAllById(clubIds).stream()
                .collect(Collectors.toMap(Club::getId, Club::getName));

        return activities.stream()
                .map(activity -> {
                    ActivityDto dto = activityMapper.toDto(activity);
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
                            clubNameMap.getOrDefault(dto.clubId(), null),
                            dto.createdBy(),
                            dto.coverImageUrl(),
                            dto.budget(),
                            dto.approvalStatus(),
                            dto.createdAt()
                    );
                })
                .collect(Collectors.toList());
    }
}

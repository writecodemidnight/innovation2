package com.campusclub.activity.application.mapper;

import com.campusclub.activity.application.dto.ActivityCreateRequest;
import com.campusclub.activity.application.dto.ActivityDto;
import com.campusclub.activity.application.dto.ActivityParticipantDto;
import com.campusclub.activity.domain.entity.Activity;
import com.campusclub.activity.domain.entity.ActivityParticipant;
import com.campusclub.user.domain.entity.User;
import org.mapstruct.*;

@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.IGNORE)
public interface ActivityMapper {

    @Mapping(target = "clubName", ignore = true)
    ActivityDto toDto(Activity activity);

    Activity toEntity(ActivityCreateRequest request);

    @Mapping(target = "id", source = "participant.id")
    @Mapping(target = "activityId", source = "participant.activityId")
    @Mapping(target = "userId", source = "participant.userId")
    @Mapping(target = "status", source = "participant.status")
    @Mapping(target = "registeredAt", source = "participant.registeredAt")
    @Mapping(target = "checkedInAt", source = "participant.checkedInAt")
    @Mapping(target = "username", expression = "java(user != null ? user.getUsername() : null)")
    @Mapping(target = "nickname", expression = "java(user != null ? user.getNickname() : null)")
    @Mapping(target = "avatarUrl", expression = "java(user != null ? user.getAvatarUrl() : null)")
    ActivityParticipantDto toParticipantDto(ActivityParticipant participant, User user);
}

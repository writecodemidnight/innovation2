package com.campusclub.user.application.mapper;

import com.campusclub.club.domain.repository.ClubMemberRepository;
import com.campusclub.user.application.dto.UserDto;
import com.campusclub.user.application.dto.UserUpdateRequest;
import com.campusclub.user.domain.entity.User;
import org.mapstruct.*;
import org.springframework.beans.factory.annotation.Autowired;

@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.IGNORE)
public abstract class UserMapper {

    @Autowired
    protected ClubMemberRepository clubMemberRepository;

    public UserDto toDto(User user) {
        Long clubId = clubMemberRepository.findByUserId(user.getId()).stream()
                .findFirst()
                .map(m -> m.getClubId())
                .orElse(null);

        return new UserDto(
                user.getId(),
                user.getStudentId(),
                user.getUsername(),
                user.getNickname(),
                user.getAvatarUrl(),
                user.getPhone(),
                user.getEmail(),
                user.getRole(),
                user.getStatus(),
                user.getCreatedAt(),
                clubId
        );
    }

    @BeanMapping(nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.IGNORE)
    public abstract void updateEntityFromRequest(UserUpdateRequest request, @MappingTarget User user);
}

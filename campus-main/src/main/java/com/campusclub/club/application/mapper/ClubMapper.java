package com.campusclub.club.application.mapper;

import com.campusclub.club.application.dto.ClubCreateRequest;
import com.campusclub.club.application.dto.ClubDto;
import com.campusclub.club.application.dto.ClubMemberDto;
import com.campusclub.club.domain.entity.Club;
import com.campusclub.club.domain.entity.ClubMember;
import com.campusclub.user.domain.entity.User;
import org.mapstruct.*;

@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.IGNORE)
public interface ClubMapper {

    ClubDto toDto(Club club);

    Club toEntity(ClubCreateRequest request);

    @Mapping(target = "username", expression = "java(user != null ? user.getUsername() : null)")
    @Mapping(target = "nickname", expression = "java(user != null ? user.getNickname() : null)")
    ClubMemberDto toMemberDto(ClubMember member, User user);
}

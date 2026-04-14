package com.campusclub.club.domain.repository;

import com.campusclub.club.domain.entity.ClubMember;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ClubMemberRepository extends JpaRepository<ClubMember, Long> {

    List<ClubMember> findByClubId(Long clubId);

    List<ClubMember> findByUserId(Long userId);

    Optional<ClubMember> findByClubIdAndUserId(Long clubId, Long userId);

    boolean existsByClubIdAndUserId(Long clubId, Long userId);

    long countByClubId(Long clubId);

    List<ClubMember> findByClubIdAndRole(Long clubId, ClubMember.MemberRole role);
}

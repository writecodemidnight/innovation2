package com.campusclub.club.application.service;

import com.campusclub.activity.domain.repository.ActivityRepository;
import com.campusclub.club.application.dto.*;
import com.campusclub.club.application.mapper.ClubMapper;
import com.campusclub.club.domain.entity.Club;
import com.campusclub.club.domain.entity.ClubMember;
import com.campusclub.club.domain.repository.ClubMemberRepository;
import com.campusclub.club.domain.repository.ClubRepository;
import com.campusclub.user.domain.entity.User;
import com.campusclub.user.domain.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class ClubApplicationService {

    private final ClubRepository clubRepository;
    private final ClubMemberRepository clubMemberRepository;
    private final UserRepository userRepository;
    private final ActivityRepository activityRepository;
    private final ClubMapper clubMapper;

    @Transactional(readOnly = true)
    public Page<ClubDto> listClubs(Club.ClubCategory category, Club.ClubStatus status, Pageable pageable) {
        Page<Club> clubs;
        if (category != null) {
            clubs = clubRepository.findByCategory(category, pageable);
        } else if (status != null) {
            clubs = clubRepository.findByStatus(status, pageable);
        } else {
            clubs = clubRepository.findAll(pageable);
        }
        return clubs.map(clubMapper::toDto);
    }

    @Transactional(readOnly = true)
    public ClubDto getClub(Long id) {
        Club club = clubRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("社团不存在"));
        return clubMapper.toDto(club);
    }

    @Transactional
    public ClubDto createClub(ClubCreateRequest request) {
        if (request.code() != null && clubRepository.existsByCode(request.code())) {
            throw new RuntimeException("社团代码已存在");
        }

        Club club = clubMapper.toEntity(request);
        club.setStatus(Club.ClubStatus.ACTIVE);
        club.setMemberCount(0);

        Club savedClub = clubRepository.save(club);
        return clubMapper.toDto(savedClub);
    }

    @Transactional
    public ClubDto updateClub(Long id, ClubCreateRequest request) {
        Club club = clubRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("社团不存在"));

        if (request.code() != null && !request.code().equals(club.getCode())
                && clubRepository.existsByCode(request.code())) {
            throw new RuntimeException("社团代码已存在");
        }

        club.setName(request.name());
        club.setCode(request.code());
        club.setDescription(request.description());
        club.setCategory(request.category());
        club.setLogoUrl(request.logoUrl());
        club.setPresidentId(request.presidentId());
        club.setFacultyAdvisor(request.facultyAdvisor());

        Club updatedClub = clubRepository.save(club);
        return clubMapper.toDto(updatedClub);
    }

    @Transactional
    public void deleteClub(Long id) {
        Club club = clubRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("社团不存在"));
        club.setDeleted(true);
        clubRepository.save(club);
    }

    @Transactional(readOnly = true)
    public List<ClubMemberDto> listClubMembers(Long clubId) {
        List<ClubMember> members = clubMemberRepository.findByClubId(clubId);
        return members.stream()
                .map(member -> {
                    User user = userRepository.findById(member.getUserId()).orElse(null);
                    return clubMapper.toMemberDto(member, user);
                })
                .toList();
    }

    @Transactional
    public void addClubMember(Long clubId, Long userId, ClubMember.MemberRole role) {
        if (clubMemberRepository.existsByClubIdAndUserId(clubId, userId)) {
            throw new RuntimeException("该用户已是社团成员");
        }

        ClubMember member = ClubMember.builder()
                .clubId(clubId)
                .userId(userId)
                .role(role != null ? role : ClubMember.MemberRole.MEMBER)
                .build();

        clubMemberRepository.save(member);

        Club club = clubRepository.findById(clubId).orElseThrow();
        club.setMemberCount((int) clubMemberRepository.countByClubId(clubId));
        clubRepository.save(club);
    }

    @Transactional
    public void removeClubMember(Long clubId, Long userId) {
        ClubMember member = clubMemberRepository.findByClubIdAndUserId(clubId, userId)
                .orElseThrow(() -> new RuntimeException("该用户不是社团成员"));

        clubMemberRepository.delete(member);

        Club club = clubRepository.findById(clubId).orElseThrow();
        club.setMemberCount((int) clubMemberRepository.countByClubId(clubId));
        clubRepository.save(club);
    }

    @Transactional(readOnly = true)
    public ClubStatsDto getClubStats(Long clubId) {
        // 活动总数
        Integer activityCount = activityRepository.countByClubId(clubId);

        // 总参与人数
        Integer totalParticipants = activityRepository.sumParticipantsByClubId(clubId);

        // 待审批活动数
        Integer pendingCount = activityRepository.countPendingByClubId(clubId);

        // 进行中活动数
        Integer ongoingCount = activityRepository.countOngoingByClubId(clubId, LocalDateTime.now());

        // 已完成活动数
        Integer completedCount = activityRepository.countCompletedByClubId(clubId);

        return ClubStatsDto.builder()
                .activityCount(activityCount != null ? activityCount : 0)
                .totalParticipants(totalParticipants != null ? totalParticipants : 0)
                .pendingCount(pendingCount != null ? pendingCount : 0)
                .ongoingCount(ongoingCount != null ? ongoingCount : 0)
                .completedCount(completedCount != null ? completedCount : 0)
                .build();
    }

    /**
     * 根据用户ID查询所属社团（用于社长查询自己管理的社团）
     * 如果没有社团，返回null而不是抛出异常
     */
    @Transactional(readOnly = true)
    public ClubDto getClubByUserId(Long userId) {
        log.info("查询用户所属社团, userId: {}", userId);

        if (userId == null) {
            log.error("用户ID为空");
            throw new RuntimeException("用户未登录");
        }

        // 通过 presidentId 查询社团（社团端只有社长使用）
        List<Club> clubs = clubRepository.findByPresidentId(userId);
        log.info("找到 {} 个社团", clubs.size());

        if (clubs.isEmpty()) {
            log.warn("用户 {} 没有所属社团", userId);
            // 返回null，让前端显示空状态
            return null;
        }

        Club club = clubs.get(0);
        log.info("返回社团: id={}, name={}", club.getId(), club.getName());

        // 返回第一个（通常一个社长只管理一个社团）
        return clubMapper.toDto(club);
    }
}

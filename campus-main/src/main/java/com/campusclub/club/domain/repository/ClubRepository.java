package com.campusclub.club.domain.repository;

import com.campusclub.club.domain.entity.Club;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ClubRepository extends JpaRepository<Club, Long> {

    Optional<Club> findByCode(String code);

    Page<Club> findByStatus(Club.ClubStatus status, Pageable pageable);

    Page<Club> findByCategory(Club.ClubCategory category, Pageable pageable);

    List<Club> findByPresidentId(Long presidentId);

    boolean existsByCode(String code);
}

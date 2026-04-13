package com.campusclub.db.repository;

import com.campusclub.common.model.BaseEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.NoRepositoryBean;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@NoRepositoryBean
public interface BaseRepository<T extends BaseEntity> extends JpaRepository<T, Long> {

    @Query("SELECT e FROM #{#entityName} e WHERE e.deleted = false AND e.id = :id")
    Optional<T> findActiveById(Long id);

    @Query("SELECT e FROM #{#entityName} e WHERE e.deleted = false")
    List<T> findAllActive();

    @Transactional
    @Modifying
    @Query("UPDATE #{#entityName} e SET e.deleted = true WHERE e.id = :id")
    void softDeleteById(Long id);

    @Query("SELECT COUNT(e) FROM #{#entityName} e WHERE e.deleted = false")
    long countActive();
}
package com.campusclub.resource.domain.repository;

import com.campusclub.resource.domain.entity.Resource;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ResourceRepository extends JpaRepository<Resource, Long> {

    /**
     * 根据类型查询可用资源
     */
    List<Resource> findByResourceTypeAndStatusAndDeletedFalse(
            String resourceType,
            String status
    );

    /**
     * 查询所有可用资源
     */
    List<Resource> findByStatusAndDeletedFalse(String status);

    /**
     * 根据名称模糊查询
     */
    @Query("SELECT r FROM Resource r WHERE r.deleted = false AND r.name LIKE %:keyword%")
    List<Resource> findByNameContaining(@Param("keyword") String keyword);
}

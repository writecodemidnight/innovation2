package com.campusclub.fund.repository;

import com.campusclub.fund.domain.entity.FundApplication;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * 资金申请表仓库接口
 */
@Repository
public interface FundApplicationRepository extends JpaRepository<FundApplication, Long> {

    /**
     * 根据社团ID查询资金申请列表
     */
    Page<FundApplication> findByClubIdOrderByCreatedAtDesc(Long clubId, Pageable pageable);

    /**
     * 根据申请人ID查询资金申请列表
     */
    Page<FundApplication> findByApplicantIdOrderByCreatedAtDesc(Long applicantId, Pageable pageable);

    /**
     * 根据状态查询资金申请列表
     */
    Page<FundApplication> findByStatusOrderByCreatedAtDesc(FundApplication.FundStatus status, Pageable pageable);

    /**
     * 根据社团ID和状态查询
     */
    Page<FundApplication> findByClubIdAndStatusOrderByCreatedAtDesc(Long clubId, FundApplication.FundStatus status, Pageable pageable);

    /**
     * 查询待审批的申请
     */
    @Query("SELECT fa FROM FundApplication fa WHERE fa.status = 'PENDING' ORDER BY fa.createdAt ASC")
    List<FundApplication> findPendingApplications();

    /**
     * 统计社团的资金申请数量
     */
    long countByClubId(Long clubId);

    /**
     * 统计社团的已批准资金总额
     */
    @Query("SELECT COALESCE(SUM(fa.amount), 0) FROM FundApplication fa WHERE fa.club.id = :clubId AND fa.status = 'APPROVED'")
    java.math.BigDecimal sumApprovedAmountByClubId(@Param("clubId") Long clubId);

    /**
     * 查询某活动的资金申请
     */
    List<FundApplication> findByActivityId(Long activityId);

    /**
     * 根据状态统计数量
     */
    long countByStatus(FundApplication.FundStatus status);

    /**
     * 查询非指定状态的资金申请
     */
    List<FundApplication> findByStatusNot(FundApplication.FundStatus status);
}

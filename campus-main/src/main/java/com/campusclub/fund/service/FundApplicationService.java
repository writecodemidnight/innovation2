package com.campusclub.fund.service;

import com.campusclub.fund.domain.entity.FundApplication;
import com.campusclub.fund.dto.FundApplicationDTO;
import com.campusclub.fund.dto.FundApplyRequest;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

/**
 * 资金申请服务接口
 */
public interface FundApplicationService {

    /**
     * 提交资金申请
     *
     * @param request 申请请求
     * @param clubId  社团ID
     * @param userId  申请人ID
     * @return 申请结果
     */
    FundApplicationDTO apply(FundApplyRequest request, Long clubId, Long userId);

    /**
     * 获取资金申请详情
     *
     * @param id 申请ID
     * @return 申请详情
     */
    FundApplicationDTO getApplication(Long id);

    /**
     * 获取社团的资金申请列表
     *
     * @param clubId   社团ID
     * @param pageable 分页参数
     * @return 申请列表
     */
    Page<FundApplicationDTO> getClubApplications(Long clubId, Pageable pageable);

    /**
     * 获取用户的资金申请列表
     *
     * @param userId   用户ID
     * @param pageable 分页参数
     * @return 申请列表
     */
    Page<FundApplicationDTO> getUserApplications(Long userId, Pageable pageable);

    /**
     * 获取所有待审批的申请
     *
     * @param pageable 分页参数
     * @return 申请列表
     */
    Page<FundApplicationDTO> getPendingApplications(Pageable pageable);

    /**
     * 审批资金申请
     *
     * @param id         申请ID
     * @param approved   是否通过
     * @param comment    审批意见
     * @param reviewerId 审批人ID
     * @return 审批结果
     */
    FundApplicationDTO review(Long id, boolean approved, String comment, Long reviewerId);

    /**
     * 取消资金申请
     *
     * @param id     申请ID
     * @param userId 用户ID
     * @param reason 取消原因
     */
    void cancel(Long id, Long userId, String reason);

    /**
     * 将实体转换为DTO
     *
     * @param application 实体
     * @return DTO
     */
    FundApplicationDTO toDTO(FundApplication application);
}

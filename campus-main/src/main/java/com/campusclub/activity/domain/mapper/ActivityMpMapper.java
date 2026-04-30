package com.campusclub.activity.domain.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.campusclub.activity.domain.entity.Activity;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Mapper
public interface ActivityMpMapper extends BaseMapper<Activity> {

    /**
     * 分页查询指定社团的活动
     */
    @Select("""
        SELECT a.* FROM activities a
        WHERE a.club_id = #{clubId}
          AND a.deleted = false
        ORDER BY a.created_at DESC
        """)
    IPage<Activity> findByClubIdPaged(Page<Activity> page, @Param("clubId") Long clubId);

    /**
     * 查询即将开始的活动
     */
    @Select("""
        SELECT a.* FROM activities a
        WHERE a.status = 'REGISTERING'
          AND a.start_time BETWEEN #{now} AND #{future}
          AND a.deleted = false
        ORDER BY a.start_time ASC
        """)
    List<Activity> findUpcomingActivities(@Param("now") LocalDateTime now,
                                           @Param("future") LocalDateTime future);

    /**
     * 统计各类型活动数量
     */
    @Select("""
        SELECT a.activity_type, COUNT(*) as cnt
        FROM activities a
        WHERE a.deleted = false
        GROUP BY a.activity_type
        ORDER BY cnt DESC
        """)
    List<Map<String, Object>> countByActivityType();
}

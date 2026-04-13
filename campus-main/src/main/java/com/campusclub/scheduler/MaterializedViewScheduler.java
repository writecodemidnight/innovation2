package com.campusclub.scheduler;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

/**
 * 物化视图刷新调度器
 * 定时刷新分析用物化视图，保持数据同步
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class MaterializedViewScheduler {

    private final JdbcTemplate jdbcTemplate;

    /**
     * 每小时刷新一次物化视图
     * 在每小时第5分钟执行，避开整点高峰
     */
    @Scheduled(cron = "0 5 * * * *")
    public void refreshMaterializedViews() {
        log.info("开始刷新物化视图...");

        try {
            // 刷新活动统计物化视图
            refreshActivityStatsView();

            // 刷新资源利用率物化视图
            refreshResourceUtilizationView();

            // 刷新社团活跃度物化视图
            refreshClubActivityView();

            log.info("物化视图刷新完成");
        } catch (Exception e) {
            log.error("刷新物化视图时发生错误: {}", e.getMessage(), e);
        }
    }

    private void refreshActivityStatsView() {
        try {
            // 检查物化视图是否存在
            String checkSql = "SELECT COUNT(*) FROM pg_matviews WHERE matviewname = 'activity_stats_mv'";
            Integer count = jdbcTemplate.queryForObject(checkSql, Integer.class);

            if (count != null && count > 0) {
                jdbcTemplate.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY analytics.activity_stats_mv");
                log.debug("成功刷新 activity_stats_mv");
            } else {
                log.debug("物化视图 activity_stats_mv 不存在，跳过刷新");
            }
        } catch (Exception e) {
            log.warn("刷新 activity_stats_mv 失败: {}", e.getMessage());
        }
    }

    private void refreshResourceUtilizationView() {
        try {
            String checkSql = "SELECT COUNT(*) FROM pg_matviews WHERE matviewname = 'resource_utilization_mv'";
            Integer count = jdbcTemplate.queryForObject(checkSql, Integer.class);

            if (count != null && count > 0) {
                jdbcTemplate.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY analytics.resource_utilization_mv");
                log.debug("成功刷新 resource_utilization_mv");
            } else {
                log.debug("物化视图 resource_utilization_mv 不存在，跳过刷新");
            }
        } catch (Exception e) {
            log.warn("刷新 resource_utilization_mv 失败: {}", e.getMessage());
        }
    }

    private void refreshClubActivityView() {
        try {
            String checkSql = "SELECT COUNT(*) FROM pg_matviews WHERE matviewname = 'club_activity_mv'";
            Integer count = jdbcTemplate.queryForObject(checkSql, Integer.class);

            if (count != null && count > 0) {
                jdbcTemplate.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY analytics.club_activity_mv");
                log.debug("成功刷新 club_activity_mv");
            } else {
                log.debug("物化视图 club_activity_mv 不存在，跳过刷新");
            }
        } catch (Exception e) {
            log.warn("刷新 club_activity_mv 失败: {}", e.getMessage());
        }
    }
}

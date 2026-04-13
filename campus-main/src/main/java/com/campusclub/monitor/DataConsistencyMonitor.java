// campus-main/src/main/java/com/campusclub/monitor/DataConsistencyMonitor.java
package com.campusclub.monitor;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.util.Arrays;
import java.util.List;

@Component
@RequiredArgsConstructor
@Slf4j
public class DataConsistencyMonitor {

    private final JdbcTemplate jdbcTemplate;

    @Scheduled(cron = "0 30 2 * * *")
    public void checkDataConsistency() {
        log.info("开始检查数据一致性...");

        List<ConsistencyCheck> checks = Arrays.asList(
            new ConsistencyCheck(
                "activities",
                "SELECT COUNT(*) FROM public.activities",
                "SELECT COUNT(*) FROM analytics.activity_facts"
            ),
            new ConsistencyCheck(
                "resource_reservations",
                "SELECT COUNT(*) FROM public.resource_reservations",
                "SELECT COUNT(*) FROM analytics.resource_utilization"
            )
        );

        for (ConsistencyCheck check : checks) {
            try {
                Long sourceCount = jdbcTemplate.queryForObject(check.getSourceQuery(), Long.class);
                Long targetCount = jdbcTemplate.queryForObject(check.getTargetQuery(), Long.class);

                // 处理null情况
                sourceCount = sourceCount != null ? sourceCount : 0L;
                targetCount = targetCount != null ? targetCount : 0L;

                if (!sourceCount.equals(targetCount)) {
                    sendAlert(check.getCheckName(), sourceCount, targetCount);
                } else {
                    log.info("数据一致性检查通过 [{}]: source={}, target={}",
                        check.getCheckName(), sourceCount, targetCount);
                }
            } catch (Exception e) {
                log.error("数据一致性检查失败 [{}]: {}", check.getCheckName(), e.getMessage(), e);
            }
        }

        log.info("数据一致性检查完成");
    }

    private void sendAlert(String checkName, Long sourceCount, Long targetCount) {
        log.error("数据不一致告警 [{}]: source_count={}, target_count={}, diff={}",
            checkName, sourceCount, targetCount, Math.abs(sourceCount - targetCount));
        // 这里可以扩展为发送邮件、短信或通知到监控系统
    }

    @Data
    @AllArgsConstructor
    private static class ConsistencyCheck {
        private String checkName;
        private String sourceQuery;
        private String targetQuery;
    }
}

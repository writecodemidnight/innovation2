// campus-main/src/test/java/com/campusclub/monitor/DataConsistencyMonitorTest.java
package com.campusclub.monitor;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.jdbc.core.JdbcTemplate;

import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class DataConsistencyMonitorTest {

    @Mock
    private JdbcTemplate jdbcTemplate;

    @InjectMocks
    private DataConsistencyMonitor monitor;

    @Test
    void testCheckDataConsistency_AllConsistent() {
        // Given: 所有表的数据一致
        when(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM public.activities", Long.class)).thenReturn(100L);
        when(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM analytics.activity_facts", Long.class)).thenReturn(100L);
        when(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM public.resource_reservations", Long.class)).thenReturn(50L);
        when(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM analytics.resource_utilization", Long.class)).thenReturn(50L);

        // When
        monitor.checkDataConsistency();

        // Then: 验证所有查询都被执行
        verify(jdbcTemplate, times(4)).queryForObject(anyString(), eq(Long.class));
    }

    @Test
    void testCheckDataConsistency_ActivitiesInconsistent() {
        // Given: activities表数据不一致
        when(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM public.activities", Long.class)).thenReturn(100L);
        when(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM analytics.activity_facts", Long.class)).thenReturn(95L);
        when(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM public.resource_reservations", Long.class)).thenReturn(50L);
        when(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM analytics.resource_utilization", Long.class)).thenReturn(50L);

        // When
        monitor.checkDataConsistency();

        // Then: 验证所有查询都被执行，即使发现不一致
        verify(jdbcTemplate, times(4)).queryForObject(anyString(), eq(Long.class));
    }

    @Test
    void testCheckDataConsistency_ResourceReservationsInconsistent() {
        // Given: resource_reservations表数据不一致
        when(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM public.activities", Long.class)).thenReturn(100L);
        when(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM analytics.activity_facts", Long.class)).thenReturn(100L);
        when(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM public.resource_reservations", Long.class)).thenReturn(50L);
        when(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM analytics.resource_utilization", Long.class)).thenReturn(48L);

        // When
        monitor.checkDataConsistency();

        // Then: 验证所有查询都被执行
        verify(jdbcTemplate, times(4)).queryForObject(anyString(), eq(Long.class));
    }

    @Test
    void testCheckDataConsistency_BothInconsistent() {
        // Given: 两个表都数据不一致
        when(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM public.activities", Long.class)).thenReturn(100L);
        when(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM analytics.activity_facts", Long.class)).thenReturn(90L);
        when(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM public.resource_reservations", Long.class)).thenReturn(50L);
        when(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM analytics.resource_utilization", Long.class)).thenReturn(45L);

        // When
        monitor.checkDataConsistency();

        // Then: 验证所有查询都被执行
        verify(jdbcTemplate, times(4)).queryForObject(anyString(), eq(Long.class));
    }

    @Test
    void testCheckDataConsistency_DatabaseException() {
        // Given: 数据库查询异常
        when(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM public.activities", Long.class))
            .thenThrow(new RuntimeException("Database connection failed"));

        // When
        monitor.checkDataConsistency();

        // Then: 验证异常被捕获，至少执行了第一个查询
        verify(jdbcTemplate, atLeast(1)).queryForObject(anyString(), eq(Long.class));
    }

    @Test
    void testCheckDataConsistency_NullCounts() {
        // Given: 查询返回null（异常情况）
        when(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM public.activities", Long.class)).thenReturn(null);
        when(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM analytics.activity_facts", Long.class)).thenReturn(100L);
        when(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM public.resource_reservations", Long.class)).thenReturn(50L);
        when(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM analytics.resource_utilization", Long.class)).thenReturn(50L);

        // When
        monitor.checkDataConsistency();

        // Then: 验证所有查询都被执行
        verify(jdbcTemplate, times(4)).queryForObject(anyString(), eq(Long.class));
    }
}

package com.campusclub.integration;

import com.campusclub.config.OpenApiConfig;
import com.campusclub.config.SchedulingConfig;
import com.campusclub.exception.GlobalExceptionHandler;
import com.campusclub.scheduler.MaterializedViewScheduler;
import com.campusclub.monitor.DataConsistencyMonitor;
import com.campusclub.dto.ApiResponse;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.ApplicationContext;
import org.springframework.test.context.ActiveProfiles;
import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
@ActiveProfiles("test")
class FirstPhaseIntegrationTest {

    @Autowired
    private ApplicationContext context;

    @Test
    void testAllComponentsLoaded() {
        // 验证所有关键组件都已加载
        assertNotNull(context.getBean(OpenApiConfig.class));
        assertNotNull(context.getBean(SchedulingConfig.class));
        assertNotNull(context.getBean(GlobalExceptionHandler.class));
        assertNotNull(context.getBean(MaterializedViewScheduler.class));
        assertNotNull(context.getBean(DataConsistencyMonitor.class));
    }

    @Test
    void testApiResponseStructure() {
        ApiResponse<String> successResponse = ApiResponse.success("test");
        assertTrue(successResponse.isSuccess());
        assertEquals("SUCCESS", successResponse.getCode());

        ApiResponse<?> errorResponse = ApiResponse.error("TEST_ERROR", "测试错误");
        assertFalse(errorResponse.isSuccess());
        assertEquals("TEST_ERROR", errorResponse.getCode());
    }
}

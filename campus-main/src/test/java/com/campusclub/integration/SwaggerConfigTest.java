package com.campusclub.integration;

import io.swagger.v3.oas.models.OpenAPI;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
@ActiveProfiles("test")
class SwaggerConfigTest {

    @Autowired(required = false)
    private OpenAPI openAPI;

    @Test
    void testSwaggerConfigLoaded() {
        assertNotNull(openAPI, "OpenAPI配置未加载");
        assertEquals("校园社团活动评估系统API", openAPI.getInfo().getTitle());
        assertEquals("1.0.0", openAPI.getInfo().getVersion());
        assertTrue(openAPI.getTags().size() >= 4, "至少应配置4个API标签");
    }
}

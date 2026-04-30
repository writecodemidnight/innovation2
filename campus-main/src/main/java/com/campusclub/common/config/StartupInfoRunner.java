package com.campusclub.common.config;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.core.env.Environment;
import org.springframework.stereotype.Component;

import javax.sql.DataSource;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.sql.DatabaseMetaData;
import java.sql.SQLException;

/**
 * 应用启动信息输出
 * 在应用启动成功后打印详细的启动信息和配置
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class StartupInfoRunner implements CommandLineRunner {

    private final Environment env;
    private final DataSource dataSource;

    @Override
    public void run(String... args) throws Exception {
        printStartupBanner();
        printApplicationInfo();
        printDatabaseInfo();
        printApiDocsInfo();
        printSecurityInfo();
        printStartupSuccess();
    }

    private void printStartupBanner() {
        log.info("""

                ╔══════════════════════════════════════════════════════════════════╗
                ║                                                                  ║
                ║           🎓 校园社团活动效果评估与资源优化配置系统 🎓              ║
                ║                                                                  ║
                ║              Campus Club Activity Management System              ║
                ║                                                                  ║
                ╚══════════════════════════════════════════════════════════════════╝
                """);
    }

    private void printApplicationInfo() throws UnknownHostException {
        String appName = env.getProperty("spring.application.name", "campus-main");
        String port = env.getProperty("server.port", "8080");
        String contextPath = env.getProperty("server.servlet.context-path", "");
        String activeProfile = String.join(", ", env.getActiveProfiles());
        if (activeProfile.isEmpty()) {
            activeProfile = "default";
        }

        String hostAddress = InetAddress.getLocalHost().getHostAddress();
        String hostName = InetAddress.getLocalHost().getHostName();

        log.info("""
                📋 应用配置信息:
                   ├── 应用名称: {}
                   ├── 运行环境: {}
                   ├── 服务端口: {}
                   ├── 上下文路径: {}
                   ├── 本机地址: {} ({})
                   └── 访问地址: http://localhost:{}{}
                """, appName, activeProfile, port, contextPath.isEmpty() ? "/" : contextPath,
                hostAddress, hostName, port, contextPath);
    }

    private void printDatabaseInfo() {
        try {
            DatabaseMetaData metaData = dataSource.getConnection().getMetaData();
            String dbUrl = metaData.getURL();
            String dbProductName = metaData.getDatabaseProductName();
            String dbProductVersion = metaData.getDatabaseProductVersion();

            // 隐藏密码敏感信息
            String displayUrl = dbUrl.replaceAll("password=([^&]*)", "password=***");

            log.info("""
                    🗄️  数据库连接信息:
                       ├── 数据库类型: {}
                       ├── 数据库版本: {}
                       └── 连接URL: {}
                    """, dbProductName, dbProductVersion, displayUrl);
        } catch (SQLException e) {
            log.warn("⚠️  无法获取数据库信息: {}", e.getMessage());
        }
    }

    private void printApiDocsInfo() {
        String port = env.getProperty("server.port", "8080");
        String contextPath = env.getProperty("server.servlet.context-path", "");

        log.info("""
                📚 API文档地址:
                   ├── Swagger UI: http://localhost:{}{}/swagger-ui/index.html
                   └── OpenAPI JSON: http://localhost:{}{}/v3/api-docs
                """, port, contextPath, port, contextPath);
    }

    private void printSecurityInfo() {
        String jwtEnabled = env.getProperty("jwt.enabled", "true");
        String jwtExpiration = env.getProperty("jwt.access-token.expiration", "3600000");

        log.info("""
                🔐 安全配置信息:
                   ├── JWT认证: {}
                   └── Token过期时间: {} ms ({} 分钟)
                """,
                "true".equals(jwtEnabled) ? "✅ 已启用" : "❌ 已禁用",
                jwtExpiration,
                Long.parseLong(jwtExpiration) / 60000);
    }

    private void printStartupSuccess() {
        log.info("""
                ╔══════════════════════════════════════════════════════════════════╗
                ║                                                                  ║
                ║                    ✅ 应用启动成功! (Startup Success)              ║
                ║                                                                  ║
                ╚══════════════════════════════════════════════════════════════════╝
                """);
    }
}

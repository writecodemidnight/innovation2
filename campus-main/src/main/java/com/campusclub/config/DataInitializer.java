package com.campusclub.config;

import com.campusclub.user.domain.entity.User;
import com.campusclub.user.domain.repository.UserRepository;
import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

@Slf4j
@Component
@RequiredArgsConstructor
public class DataInitializer implements CommandLineRunner {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    @PersistenceContext
    private EntityManager entityManager;

    @Override
    @Transactional
    public void run(String... args) {
        log.info("检查测试用户数据...");

        // 只创建不存在的测试用户，不删除现有用户
        String[][] testUsers = {
                {"admin", "admin123", "admin@campus.edu", "系统管理员", "ADMIN001", "ADMIN"},
                {"admin2", "admin123", "admin2@campus.edu", "系统管理员2", "ADMIN002", "ADMIN"},
                {"club1", "admin123", "club1@campus.edu", "社团管理员", "2021001", "CLUB_PRESIDENT"},
                {"club2", "club2", "club2@campus.edu", "社团管理员2", "2021005", "CLUB_PRESIDENT"},
                {"student1", "admin123", "stu1@campus.edu", "张三", "2021002", "STUDENT"},
                {"student2", "admin123", "stu2@campus.edu", "李四", "2021004", "STUDENT"}
        };

        for (String[] userData : testUsers) {
            String username = userData[0];
            if (userRepository.findByUsername(username).isEmpty()) {
                User user = User.builder()
                        .username(username)
                        .password(passwordEncoder.encode(userData[1]))
                        .email(userData[2])
                        .nickname(userData[3])
                        .studentId(userData[4])
                        .role(User.UserRole.valueOf(userData[5]))
                        .status(User.UserStatus.ACTIVE)
                        .build();
                userRepository.save(user);
                log.info("创建用户: {}", username);
            }
        }

        log.info("测试用户数据检查完成！");
    }
}

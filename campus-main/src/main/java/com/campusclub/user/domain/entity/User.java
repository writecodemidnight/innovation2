package com.campusclub.user.domain.entity;

import com.campusclub.common.model.BaseEntity;
import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "users")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User extends BaseEntity {

    @Column(name = "openid", unique = true, length = 100)
    private String openid;

    @Column(name = "student_id", unique = true, length = 50)
    private String studentId;

    @Column(name = "username", nullable = false, length = 50)
    private String username;

    @Column(name = "nickname", length = 50)
    private String nickname;

    @Column(name = "avatar_url", length = 500)
    private String avatarUrl;

    @Column(name = "phone", length = 20)
    private String phone;

    @Column(name = "email", length = 100)
    private String email;

    @Column(name = "password", length = 100)
    private String password;

    @Builder.Default
    @Enumerated(EnumType.STRING)
    @Column(name = "role", nullable = false, length = 20)
    private UserRole role = UserRole.STUDENT;

    @Builder.Default
    @Enumerated(EnumType.STRING)
    @Column(name = "status", length = 20)
    private UserStatus status = UserStatus.ACTIVE;

    public enum UserRole {
        STUDENT, CLUB_MEMBER, CLUB_MANAGER, CLUB_PRESIDENT, ADMIN, SUPER_ADMIN
    }

    public enum UserStatus {
        ACTIVE, INACTIVE
    }
}

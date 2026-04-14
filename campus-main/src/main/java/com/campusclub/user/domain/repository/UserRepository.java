package com.campusclub.user.domain.repository;

import com.campusclub.user.domain.entity.User;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    Optional<User> findByOpenid(String openid);

    Optional<User> findByStudentId(String studentId);

    Optional<User> findByUsername(String username);

    boolean existsByOpenid(String openid);

    boolean existsByStudentId(String studentId);

    Page<User> findByRole(User.UserRole role, Pageable pageable);
}

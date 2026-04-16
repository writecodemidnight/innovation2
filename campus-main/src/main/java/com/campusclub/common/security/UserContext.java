package com.campusclub.common.security;

import com.campusclub.club.domain.entity.ClubMember;
import com.campusclub.club.domain.repository.ClubMemberRepository;
import com.campusclub.user.domain.entity.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;

import java.util.Optional;

/**
 * 用户上下文工具类
 * 用于获取当前登录用户的信息
 */
@Component
public class UserContext {

    /**
     * 获取当前登录用户ID
     *
     * @return 当前用户ID
     * @throws UnauthorizedException 用户未登录时抛出
     */
    public static Long getCurrentUserId() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth == null || !auth.isAuthenticated()) {
            throw new UnauthorizedException("用户未登录");
        }

        Object principal = auth.getPrincipal();
        if (principal instanceof Long) {
            return (Long) principal;
        }

        throw new IllegalStateException("无法获取当前用户ID");
    }

    /**
     * 获取当前登录用户的角色
     *
     * @return 角色字符串（如：STUDENT, CLUB_MANAGER, ADMIN）
     * @throws UnauthorizedException 用户未登录时抛出
     */
    public static String getCurrentUserRole() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth == null || !auth.isAuthenticated()) {
            throw new UnauthorizedException("用户未登录");
        }

        return auth.getAuthorities().stream()
                .findFirst()
                .map(authority -> authority.getAuthority().replace("ROLE_", ""))
                .orElseThrow(() -> new IllegalStateException("无法获取当前用户角色"));
    }

    /**
     * 检查当前用户是否有指定角色
     *
     * @param role 角色名称
     * @return true 如果有该角色
     */
    public static boolean hasRole(String role) {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth == null || !auth.isAuthenticated()) {
            return false;
        }

        String roleWithPrefix = role.startsWith("ROLE_") ? role : "ROLE_" + role;
        return auth.getAuthorities().stream()
                .anyMatch(a -> a.getAuthority().equals(roleWithPrefix));
    }

    /**
     * 检查当前用户是否有任意指定角色
     *
     * @param roles 角色名称数组
     * @return true 如果有任意一个角色
     */
    public static boolean hasAnyRole(String... roles) {
        for (String role : roles) {
            if (hasRole(role)) {
                return true;
            }
        }
        return false;
    }

    private static ClubMemberRepository clubMemberRepository;

    /**
     * 注入 ClubMemberRepository
     * 使用 setter 注入避免循环依赖
     */
    @Autowired
    public void setClubMemberRepository(ClubMemberRepository repository) {
        UserContext.clubMemberRepository = repository;
    }

    /**
     * 获取当前用户所属社团ID
     *
     * @return 社团ID，如果没有则返回 null
     */
    public static Long getCurrentClubId() {
        Long userId = getCurrentUserId();

        if (clubMemberRepository == null) {
            throw new IllegalStateException("ClubMemberRepository 未初始化");
        }

        return clubMemberRepository.findByUserId(userId).stream()
                .findFirst()
                .map(ClubMember::getClubId)
                .orElse(null);
    }

    /**
     * 检查当前用户是否是管理员
     *
     * @return true 如果是管理员
     */
    public static boolean isAdmin() {
        return hasRole("ADMIN") || hasRole("SUPER_ADMIN");
    }

    /**
     * 检查当前用户是否是社团管理者
     *
     * @return true 如果是社团社长或经理
     */
    public static boolean isClubManager() {
        return hasAnyRole("CLUB_PRESIDENT", "CLUB_MANAGER");
    }

    /**
     * 自定义未授权异常
     */
    public static class UnauthorizedException extends RuntimeException {
        public UnauthorizedException(String message) {
            super(message);
        }
    }
}

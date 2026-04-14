package com.campusclub.user.application.service;

import com.campusclub.user.application.dto.UserDto;
import com.campusclub.user.application.dto.UserUpdateRequest;
import com.campusclub.user.application.mapper.UserMapper;
import com.campusclub.user.domain.entity.User;
import com.campusclub.user.domain.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class UserApplicationService {

    private final UserRepository userRepository;
    private final UserMapper userMapper;

    @Transactional(readOnly = true)
    public UserDto getCurrentUser(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        return userMapper.toDto(user);
    }

    @Transactional
    public UserDto updateUser(Long userId, UserUpdateRequest request) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("用户不存在"));

        userMapper.updateEntityFromRequest(request, user);
        User updatedUser = userRepository.save(user);

        return userMapper.toDto(updatedUser);
    }
}

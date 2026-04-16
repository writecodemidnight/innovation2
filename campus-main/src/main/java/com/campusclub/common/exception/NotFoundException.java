package com.campusclub.common.exception;

import org.springframework.http.HttpStatus;

/**
 * 资源未找到异常
 */
public class NotFoundException extends BusinessException {

    public NotFoundException(String message) {
        super(message, HttpStatus.NOT_FOUND, "NOT_FOUND");
    }

    public NotFoundException(String resourceType, Object identifier) {
        super(String.format("%s 不存在: %s", resourceType, identifier),
              HttpStatus.NOT_FOUND, "NOT_FOUND");
    }
}

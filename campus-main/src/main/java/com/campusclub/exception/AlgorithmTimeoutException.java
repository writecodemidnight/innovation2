package com.campusclub.exception;

public class AlgorithmTimeoutException extends RuntimeException {

    public AlgorithmTimeoutException(String message) {
        super(message);
    }

    public AlgorithmTimeoutException(String message, Throwable cause) {
        super(message, cause);
    }
}

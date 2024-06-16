package com.example.nasdaq.exception;

import org.springframework.http.HttpStatus;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public enum ErrorCode {
    BAD_REQUEST(400, HttpStatus.BAD_REQUEST,"잘못된 요청입니다."),
    UNAUTHORIZED(401, HttpStatus.UNAUTHORIZED, "승인되지 않은 접근입니다."),
    FORBIDDEN(403, HttpStatus.FORBIDDEN, "접근 권한이 없습니다."),
    NOT_FOUND(404, HttpStatus.NOT_FOUND, "요청하신 페이지를 찾을 수 없습니다."),
    CONFLICT(409, HttpStatus.CONFLICT, "요청이 현재 서버의 상태와 충돌하였습니다."),
    ;


    private final int statusCode;
    private final HttpStatus httpStatus;
    private final String message;
    
}

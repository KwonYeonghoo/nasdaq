package com.example.nasdaq.exception;

import org.springframework.http.HttpStatus;

import lombok.AllArgsConstructor;
import lombok.Getter;


// @Builder
@Getter
@AllArgsConstructor
public class ErrorResponse {
    private final int statusCode;
    private final HttpStatus httpStatus;
    private final String message;

    // public static ResponseEntity<ErrorResponse> toResponseEntity(ErrorCode errorCode) {
    //     return ResponseEntity
    //             .status(errorCode.getHttpStatus())
    //             .body(ErrorResponse.builder()
    //                     .status(errorCode.getHttpStatus())
    //                     .message(errorCode.getDetail())
    //                     .build()
    //             );
    // }
}

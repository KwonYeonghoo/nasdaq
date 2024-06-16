package com.example.nasdaq.exception;


import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.servlet.ModelAndView;
import org.springframework.web.servlet.NoHandlerFoundException;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@RestControllerAdvice
@ControllerAdvice
public class GlobalExceptionHandler{

    @ExceptionHandler(NoHandlerFoundException.class)
    public ModelAndView handleNoHandlerFoundException(NoHandlerFoundException e) {
        ErrorResponse response = new ErrorResponse(404, HttpStatus.NOT_FOUND, "페이지를 찾을 수 없습니다!");

        ModelAndView modelAndView = new ModelAndView("error");
        modelAndView.addObject("statusCode", response.getStatusCode());
        modelAndView.addObject("httpStatus", response.getHttpStatus());
        modelAndView.addObject("message", response.getMessage());
        return modelAndView;
    }

    @ExceptionHandler(CustomException.class)
    public ModelAndView handleCustomException(CustomException e){
        ErrorCode errorCode = e.getErrorCode();
        ErrorResponse response = new ErrorResponse(errorCode.getStatusCode(), errorCode.getHttpStatus(), errorCode.getMessage());

        ModelAndView modelAndView = new ModelAndView("error");
        modelAndView.addObject("statusCode", response.getStatusCode());
        modelAndView.addObject("httpStatus", response.getHttpStatus());
        modelAndView.addObject("message", response.getMessage());
        return modelAndView;
    }

    @ExceptionHandler(Exception.class)
    public ModelAndView handleAllException(Exception e){
        ErrorResponse response;
        if(e instanceof CustomException){
            CustomException ce = (CustomException) e;
            ErrorCode errorCode = ce.getErrorCode();
            response = new ErrorResponse(errorCode.getStatusCode(), errorCode.getHttpStatus(), errorCode.getMessage());
        } else if(e instanceof NoHandlerFoundException) {
            response = new ErrorResponse(404, HttpStatus.NOT_FOUND, "페이지를 찾을 수 없습니다!");
        }
        else {
            response = new ErrorResponse(500, HttpStatus.INTERNAL_SERVER_ERROR, "내부 서버 오류가 발생했습니다!");
        }
        
        ModelAndView modelAndView = new ModelAndView("error");
        modelAndView.addObject("statusCode", response.getStatusCode());
        modelAndView.addObject("httpStatus", response.getHttpStatus());
        modelAndView.addObject("message", response.getMessage());
        return modelAndView;
    }
}

package com.internpilot.backend.config;

import com.internpilot.backend.dto.ErrorResponseDTO;
import jakarta.servlet.http.HttpServletRequest;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.server.ResponseStatusException;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponseDTO> handleValidation(
            MethodArgumentNotValidException ex,
            HttpServletRequest request
    ) {
        return ResponseEntity.badRequest().body(new ErrorResponseDTO(
                "INVALID_REQUEST",
                "Request validation failed.",
                false,
                traceId()
        ));
    }

    @ExceptionHandler(ResponseStatusException.class)
    public ResponseEntity<ErrorResponseDTO> handleResponseStatus(ResponseStatusException ex) {
        HttpStatus status = HttpStatus.valueOf(ex.getStatusCode().value());
        boolean retryable = status.is5xxServerError();
        return ResponseEntity.status(status).body(new ErrorResponseDTO(
                status == HttpStatus.BAD_GATEWAY ? "AGENT_ANALYSIS_FAILED" : "REQUEST_FAILED",
                ex.getReason() == null ? "Request failed." : ex.getReason(),
                retryable,
                traceId()
        ));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponseDTO> handleUnexpected(Exception ex) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(new ErrorResponseDTO(
                "INTERNAL_SERVER_ERROR",
                "Unexpected backend error.",
                true,
                traceId()
        ));
    }

    private static String traceId() {
        return UUID.randomUUID().toString();
    }
}

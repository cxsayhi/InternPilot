package com.internpilot.backend;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;

@SpringBootApplication
@ConfigurationPropertiesScan
public class InternPilotBackendApplication {

    public static void main(String[] args) {
        SpringApplication.run(InternPilotBackendApplication.class, args);
    }
}


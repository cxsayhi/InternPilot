package com.internpilot.backend.common;

import java.util.UUID;

public final class IdGenerator {

    private IdGenerator() {
    }

    public static String prefixedId(String prefix) {
        return prefix + "_" + UUID.randomUUID();
    }
}


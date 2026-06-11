package com.internpilot.backend.user;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class UserService {

    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @Transactional
    public void ensureUserExists(String userId) {
        if (userRepository.existsById(userId)) {
            return;
        }
        String email = userId + "@local.internpilot";
        userRepository.save(new UserEntity(userId, email, userId));
    }
}


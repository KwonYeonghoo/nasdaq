package com.example.nasdaq.model.DAO.impl;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.nasdaq.exception.CustomException;
import com.example.nasdaq.model.DAO.UserDao;
import com.example.nasdaq.model.Entity.UserEntity;
import com.example.nasdaq.model.Repository.UserRepository;

@Service
public class UserDaoImpl implements UserDao{

    @Autowired
    private UserRepository userRepository;

    @Override
    public void deleteUser(String userId) {
        // TODO Auto-generated method stub
        userRepository.deleteById(userId);
    }

    @Override
    public List<UserEntity> getAllUser() {
        // TODO Auto-generated method stub
        
        return userRepository.findAll();
    }

    @Override
    public UserEntity getUserByName(String userId) {
        // TODO Auto-generated method stub
        
        return userRepository.getUserByName(userId);
    }

    @Override
    public void insertUser(UserEntity entity) throws CustomException {
        // TODO Auto-generated method stub
        userRepository.save(entity);
    }

    @Override
    public void updateUser(UserEntity entity) {
        // TODO Auto-generated method stub
        userRepository.save(entity);
    }
    
}


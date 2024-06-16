package com.example.nasdaq.model.DAO;

import java.util.List;

import com.example.nasdaq.exception.CustomException;
import com.example.nasdaq.model.Entity.UserEntity;

public interface UserDao {
    // select
    public UserEntity getUserByName(String userId);

    public List<UserEntity> getAllUser();

    // insert
    public void insertUser(UserEntity entity) throws CustomException;

    // update
    public void updateUser(UserEntity entity);

    // delete
    public void deleteUser(String userId);


    
}


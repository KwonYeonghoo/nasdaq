package com.example.nasdaq.model.DAO;

import com.example.nasdaq.model.Entity.NetworkEntity;

public interface NetworkDao {
    
    public NetworkEntity getOneNetwork(String center, String dailydate);
}

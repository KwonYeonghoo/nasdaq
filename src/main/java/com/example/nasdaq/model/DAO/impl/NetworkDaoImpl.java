package com.example.nasdaq.model.DAO.impl;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.nasdaq.model.DAO.NetworkDao;
import com.example.nasdaq.model.Entity.NetworkEntity;
import com.example.nasdaq.model.Repository.NetworkRepository;

@Service
public class NetworkDaoImpl implements NetworkDao{

    @Autowired
    private NetworkRepository networkRepository;

    @Override
    public NetworkEntity getOneNetwork(String center, String dailydate) {
        // TODO Auto-generated method stub
        NetworkEntity entity = networkRepository.findByNetworkPKCenterAndNetworkPKDailydate(center, dailydate);
        return entity;
    }
    
}

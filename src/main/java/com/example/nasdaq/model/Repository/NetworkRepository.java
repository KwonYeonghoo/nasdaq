package com.example.nasdaq.model.Repository;

import org.springframework.data.jpa.repository.JpaRepository;

import com.example.nasdaq.model.Entity.NetworkEntity;
import com.example.nasdaq.model.Entity.NetworkPK;

public interface NetworkRepository extends JpaRepository<NetworkEntity, NetworkPK>{
    
    public NetworkEntity findByNetworkPKCenterAndNetworkPKDailydate(String center, String dailydate);
}

package com.example.nasdaq.service.Impl;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.nasdaq.model.DAO.NetworkDao;
import com.example.nasdaq.model.DTO.NetworkDto;
import com.example.nasdaq.model.Entity.NetworkEntity;
import com.example.nasdaq.service.NetworkService;

@Service
public class NetworkServiceImpl implements NetworkService{
    
    @Autowired
    private NetworkDao networkDao;

    @Override
    public NetworkDto getOneNetwork(String center, String dailydate) {
        // TODO Auto-generated method stub
        NetworkEntity entity = networkDao.getOneNetwork(center, dailydate);
        NetworkDto dto = new NetworkDto();

        dto.setCenter(entity.getNetworkPK().getCenter());
        dto.setDailydate(entity.getNetworkPK().getDailydate());
        dto.setInd1(entity.getInd1());
        dto.setCorr1(entity.getCorr1());
        dto.setInd2(entity.getInd2());
        dto.setCorr2(entity.getCorr2());
        dto.setInd3(entity.getInd3());
        dto.setCorr3(entity.getCorr3());
        dto.setInd4(entity.getInd4());
        dto.setCorr4(entity.getCorr4());
        dto.setInd5(entity.getInd5());
        dto.setCorr5(entity.getCorr5());

        return dto;
    }

}

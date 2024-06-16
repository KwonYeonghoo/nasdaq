package com.example.nasdaq.service.Impl;

import java.util.ArrayList;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.nasdaq.model.DAO.WatchlistDao;
import com.example.nasdaq.model.DTO.WatchlistDto;
import com.example.nasdaq.model.Entity.WatchlistEntity;
import com.example.nasdaq.service.WatchlistService;

@Service
public class WatchlistServiceImpl implements WatchlistService{
    
    @Autowired
    private WatchlistDao watchlistDao;

    @Override
    public List<WatchlistDto> getWatchlist(String userId) {
        // TODO Auto-generated method stub
        List<WatchlistEntity> entities = watchlistDao.getWatchlist(userId);
        List<WatchlistDto> dtos = new ArrayList<>();

        for(WatchlistEntity entity : entities){
            WatchlistDto dto = new WatchlistDto();
            dto.setTicker(entity.getTicker());
            dto.setUserId(entity.getUserId());
            dto.setName(entity.getName());

            dtos.add(dto);
        }
        return dtos;
    }

    


    @Override
    public WatchlistDto getOneWatchlist(String userId, String ticker) {
        // TODO Auto-generated method stub
        WatchlistEntity entity = watchlistDao.getOneWatchlist(userId, ticker);
        WatchlistDto dto = new WatchlistDto();

        dto.setUserId(entity.getUserId());
        dto.setTicker(entity.getTicker());
        dto.setName(entity.getName());

        return dto;
    }




    @Override
    public Integer toggleWatchlist(String userId, String ticker, String name) {
        // TODO Auto-generated method stub
        WatchlistEntity entity = watchlistDao.getOneWatchlist(userId, ticker);
        if(entity == null){
            watchlistDao.addToWatchlist(userId, ticker, name);
            return 1;
        } else {
            watchlistDao.deleteFromWatchlist(userId, ticker);
            return 0;
        }
    }
    
}

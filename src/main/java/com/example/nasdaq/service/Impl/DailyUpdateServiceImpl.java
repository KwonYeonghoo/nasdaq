package com.example.nasdaq.service.Impl;

import java.util.ArrayList;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.nasdaq.model.DAO.DailyUpdatesDao;
import com.example.nasdaq.model.DTO.DailyUpdateDto;
import com.example.nasdaq.model.DTO.HottestTickersInterface;
import com.example.nasdaq.model.DTO.TopTickersInterface;
import com.example.nasdaq.model.Entity.DailyUpdateEntity;
import com.example.nasdaq.model.Repository.DailyUpdateRepository;
import com.example.nasdaq.service.DailyUpdateService;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
public class DailyUpdateServiceImpl implements DailyUpdateService{
    
    @Autowired
    private DailyUpdatesDao dailyUpdatesDao;

    @Autowired
    private DailyUpdateRepository dailyUpdateRepository;


    @Override
    public List<DailyUpdateDto> getOneDailyInfo(String ticker, String dailydate) {
        // TODO Auto-generated method stub

        List<DailyUpdateEntity> entities = dailyUpdatesDao.getOneDailyInfo(ticker, dailydate);
        List<DailyUpdateDto> dtos = new ArrayList<>();
        for(DailyUpdateEntity entity : entities) {
            DailyUpdateDto dto = new DailyUpdateDto();
        
            dto.setTicker(entity.getTicker());
            dto.setDailydate(entity.getDailydate());
            dto.setName(entity.getName());
            dto.setIndustry(entity.getIndustry());
            dto.setNews_summary(entity.getNews_summary());
            dto.setMarket_cap(entity.getMarket_cap());
            dto.setPer(entity.getPer());
            dto.setPsr(entity.getPsr());
            dto.setPbr(entity.getPbr());
            dto.setEv_ebitda(entity.getEv_ebitda());
            dto.setFluc(entity.getFluc());
            dto.setClose_price(entity.getClose_price());

            dtos.add(dto);
        }
        
        return dtos;
    }

    @Override
    public String getMostRecentDate() {
        // TODO Auto-generated method stub
        String recentDate = dailyUpdatesDao.getMostRecentDate();
        return recentDate;
    }

    @Override
    public List<String> getTickersContaining(String ticker) {
        // TODO Auto-generated method stub
        List<DailyUpdateEntity> entities = dailyUpdatesDao.getTickersContaining(ticker);
        List<String> tickers = new ArrayList<>();
        for(DailyUpdateEntity entity : entities) {
            String tick = entity.getTicker();
            // 중복으로 들어오는 값 제거
            if(!tickers.contains(tick)){
                tickers.add(tick);
            }
        }
        return tickers;
    }

    @Override
    public TopTickersInterface getBestTickersByIndustry(String industry, String dailydate) {
        // TODO Auto-generated method stub
        TopTickersInterface values = dailyUpdateRepository.findBestTickerByIndustry(industry, dailydate);
        return values;

        // String recentDate = dailyUpdatesDao.getMostRecentDate();

        // List<TopTickersEntity> entities = dailyUpdatesDao.getTop5TickersByIndustry(industry, recentDate);
        // List<TopTickersDto> dtos = new ArrayList<>();
        // for(TopTickersEntity entity : entities){
        //     TopTickersDto dto = new TopTickersDto();
        //     dto.setTicker(entity.getTicker());
        //     dto.setName(entity.getName());

        //     dtos.add(dto);
        // }
        // return dtos;
    }

    @Override
    public List<HottestTickersInterface> getTop3TickersByFluc(String dailydate) {
        // TODO Auto-generated method stub
        List<HottestTickersInterface> tickers = dailyUpdateRepository.findTop3TickerByFluc(dailydate);
        return tickers;
    }

    @Override
    public List<HottestTickersInterface> getWorst3TickersByFluc(String dailydate) {
        // TODO Auto-generated method stub
        List<HottestTickersInterface> tickers = dailyUpdateRepository.findWorst3TickerByFluc(dailydate);
        return tickers;
    }

    @Override
    public List<DailyUpdateDto> getWeeklyInfo(String ticker) {
        // TODO Auto-generated method stub
        List<DailyUpdateEntity> entities = dailyUpdatesDao.getWeeklyInfo(ticker);
        List<DailyUpdateDto> dtos = new ArrayList<>();

        for(DailyUpdateEntity entity : entities){
            DailyUpdateDto dto = new DailyUpdateDto();
            dto.setTicker(entity.getTicker());
            dto.setName(entity.getName());
            dto.setDailydate(entity.getDailydate());
            dto.setIndustry(entity.getIndustry());
            dto.setPbr(entity.getPbr());
            dto.setPer(entity.getPer());
            dto.setFluc(entity.getFluc());
            dto.setClose_price(entity.getClose_price());

            dtos.add(dto);
        }
        return dtos;
    }

    
}

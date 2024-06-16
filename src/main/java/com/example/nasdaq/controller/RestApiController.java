package com.example.nasdaq.controller;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.example.nasdaq.model.DTO.DailyUpdateDto;
import com.example.nasdaq.model.DTO.IndustryDto;
import com.example.nasdaq.model.DTO.NetworkDto;
import com.example.nasdaq.model.DTO.PredictpriceDto;
import com.example.nasdaq.model.DTO.WatchlistDto;
import com.example.nasdaq.service.DailyUpdateService;
import com.example.nasdaq.service.IndustryService;
import com.example.nasdaq.service.NetworkService;
import com.example.nasdaq.service.PredictpriceService;
import com.example.nasdaq.service.WatchlistService;

import lombok.extern.slf4j.Slf4j;

@RestController
@RequestMapping("/api/v1/nasdaq")
@Slf4j
public class RestApiController {
    

    @Autowired
    private DailyUpdateService dailyUpdateService;

    @Autowired
    private IndustryService industryService;

    @Autowired
    private PredictpriceService predictpriceService;

    @Autowired
    private WatchlistService watchlistService;

    @Autowired
    private NetworkService networkService;

    // java script에서 사용할 rest handler
    @GetMapping("/search")
    public Map<String, Object> searchTickers(@RequestParam String ticker) throws Exception{
        List<String> tickers = dailyUpdateService.getTickersContaining(ticker);
        String recent_date = dailyUpdateService.getMostRecentDate();

        Map<String, Object> response = new HashMap<>();
        response.put("tickers", tickers);
        response.put("recent_date", recent_date);

        return response;
    }

    @GetMapping("/industries")
    public List<IndustryDto> industries() throws Exception {
        List<IndustryDto> dtos = industryService.getAllIndustry();
        return dtos;
    }

    @GetMapping("/industry")
    public IndustryDto industry(@RequestParam String industry) throws Exception{
        IndustryDto dto = industryService.getIndustryAvg(industry);
        return dto;
    }

    @GetMapping("/ratios")
    public DailyUpdateDto dailyUpdates(@RequestParam String ticker) throws Exception{
        String recentDate = dailyUpdateService.getMostRecentDate();
        List<DailyUpdateDto> dtos = dailyUpdateService.getOneDailyInfo(ticker, recentDate);
        DailyUpdateDto firstDto =  dtos.get(0);
        return firstDto;
    }
    
    @GetMapping("/price")
    public List<PredictpriceDto> getprice(@RequestParam String ticker) throws Exception{
        List<PredictpriceDto> dtos = predictpriceService.getTickerprice(ticker);
        log.info("dtos: " + dtos);
        return dtos;
    }

    @PostMapping("/addWatchlist")
    public ResponseEntity<Integer> toggleWatchlist(@RequestParam String userId, @RequestParam String ticker, @RequestParam String name) throws Exception{
        Integer result = watchlistService.toggleWatchlist(userId, ticker, name);
        return ResponseEntity.ok(result);
    }

    @GetMapping("/getOneWatchlist")
    public WatchlistDto getWatchlist(@RequestParam String userId, @RequestParam String ticker) throws Exception{
        WatchlistDto dto = watchlistService.getOneWatchlist(userId, ticker);
        return dto;
    }

    @GetMapping("/network")
    public NetworkDto getNetwork(@RequestParam String center) throws Exception{
        String recent_date = dailyUpdateService.getMostRecentDate();
        NetworkDto dto = networkService.getOneNetwork(center, recent_date);
        return dto;
    }
}

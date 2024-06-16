package com.example.nasdaq.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.example.nasdaq.model.DTO.StockDataDto;
import com.example.nasdaq.service.StockDataService;

@RestController
@RequestMapping("/api/v1/nasdaq")
public class stockDataController {
    
    @Autowired
    private StockDataService stockDataService;

    @GetMapping("/bollinger")
    public List<StockDataDto> getBollinger(@RequestParam String ticker) throws Exception{
        return stockDataService.getOneStockData(ticker);
    }
}

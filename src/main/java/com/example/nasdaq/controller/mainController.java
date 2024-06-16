package com.example.nasdaq.controller;


import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

import com.example.nasdaq.model.DTO.HottestTickersInterface;
import com.example.nasdaq.model.DTO.IndustryDto;
import com.example.nasdaq.model.DTO.TopTickersInterface;
import com.example.nasdaq.service.DailyUpdateService;
import com.example.nasdaq.service.IndustryService;

import lombok.extern.slf4j.Slf4j;


@RequestMapping("/v1/nasdaq")
@Controller
@Slf4j
public class mainController {

    @Autowired
    private DailyUpdateService dailyUpdateService;

    @Autowired
    private IndustryService industryService;

    @GetMapping("/main")
    public String mainPage(Model model) throws Exception{

    String recentDate = dailyUpdateService.getMostRecentDate();
    List<IndustryDto> dtos = industryService.getAllIndustry();
    Map<String, List<String>> topFive = new HashMap<>();

    int count1 = 1;
    for (IndustryDto dto : dtos) {
        String industry = dto.getIndustry();
        model.addAttribute(String.format("industry%d", count1), industry);

        TopTickersInterface ticker_name = dailyUpdateService.getBestTickersByIndustry(industry, recentDate);
        if (ticker_name != null) {
            List<String> tickerInfo = new ArrayList<>();
            String ticker = ticker_name.getTicker();
            String name = ticker_name.getName();
            tickerInfo.add(ticker);
            tickerInfo.add(name);
            topFive.put(industry, tickerInfo);

            model.addAttribute(String.format("ticker%d", count1), topFive.get(industry).get(0));
            model.addAttribute(String.format("name%d", count1), topFive.get(industry).get(1));
        } else {
            model.addAttribute(String.format("ticker%d", count1), "나스닥100에 해당 산업군의 종목이 없습니다.");
            model.addAttribute(String.format("name%d", count1), "");
        }
        
        count1++;
    }

    int count2 = 1;
    for(HottestTickersInterface hottest : dailyUpdateService.getTop3TickersByFluc(recentDate)){
        model.addAttribute(String.format("hotTicker%d", count2), hottest.getTicker());
        model.addAttribute(String.format("hotName%d", count2), hottest.getName());
        model.addAttribute(String.format("hotFluc%d", count2), hottest.getFluc());
        
        count2 ++;
    }
    return "main";
}

}

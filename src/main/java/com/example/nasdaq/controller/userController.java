package com.example.nasdaq.controller;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;

import com.example.nasdaq.config.auth.AuthUserDto;
import com.example.nasdaq.model.DTO.DailyUpdateDto;
import com.example.nasdaq.model.DTO.HottestTickersInterface;
import com.example.nasdaq.model.DTO.IndustryDto;
import com.example.nasdaq.model.DTO.TopTickersInterface;
import com.example.nasdaq.model.DTO.WatchlistDto;
import com.example.nasdaq.service.DailyUpdateService;
import com.example.nasdaq.service.EdgarReportsService;
import com.example.nasdaq.service.IndustryService;
import com.example.nasdaq.service.Nasdaq100Service;
import com.example.nasdaq.service.NetworkService;
import com.example.nasdaq.service.S3Service;
import com.example.nasdaq.service.WatchlistService;

import lombok.extern.slf4j.Slf4j;


@Controller
@RequestMapping("/user/v1/nasdaq")
@Slf4j
public class userController {
    
    @Autowired
    private S3Service s3Service;

    @Autowired
    private DailyUpdateService dailyUpdateService;

    @Autowired
    private EdgarReportsService edgarReportsService;

    @Autowired
    private IndustryService industryService;

    @Autowired
    private Nasdaq100Service nasdaq100Service;

    @Autowired
    private WatchlistService watchlistService;

    @Autowired
    private NetworkService networkService;


    private static final String BUCKET_NAME = "playdata-team1-bucket";


    @GetMapping("/main")
    public String mainPage(@AuthenticationPrincipal AuthUserDto user, Model model) throws Exception{

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
    model.addAttribute("userName", user.getUsername());

    int count2 = 1;
    for(HottestTickersInterface hottest : dailyUpdateService.getTop3TickersByFluc(recentDate)){
        model.addAttribute(String.format("hotTicker%d", count2), hottest.getTicker());
        model.addAttribute(String.format("hotName%d", count2), hottest.getName());
        model.addAttribute(String.format("hotFluc%d", count2), hottest.getFluc());
        
        count2 ++;
    }

    List<WatchlistDto> watchlists = watchlistService.getWatchlist(user.getUsername());
    model.addAttribute("watchlists", watchlists);
    return "/user/main";
    }


    @GetMapping("/details")
    public String detailsPage(@AuthenticationPrincipal AuthUserDto user, Model model, @RequestParam String ticker) throws Exception{
        String recentDate = dailyUpdateService.getMostRecentDate();
        List<DailyUpdateDto> dtos = dailyUpdateService.getOneDailyInfo(ticker, recentDate);
        DailyUpdateDto firstDto = dtos.get(0);
        if(firstDto.getNews_summary().equals("None")){
            model.addAttribute("summary", String.format("오늘은 %s 관련 뉴스가 없습니다!", ticker));
        } else {
            List<String> summary_arr = new ArrayList<>();

            for (DailyUpdateDto dto : dtos) {
                String file_path = dto.getNews_summary();
                String news_summary = s3Service.getFileFromS3(BUCKET_NAME, file_path);
                summary_arr.add(news_summary);
            }

            model.addAttribute("summary", summary_arr);
        }
        log.info("[detailsController] firstDto >>> "+firstDto);
        log.info("[detailsController] industry >>> "+firstDto.getIndustry());

        IndustryDto industryDto = industryService.getIndustryAvg(firstDto.getIndustry());
        log.info("[detailsController] industryDto >>> "+industryDto);

        model.addAttribute("Industry", industryDto.getIndustry());
        model.addAttribute("avgPER", roundToTwoDecimalPlaces(industryDto.getAvgPER()));
        model.addAttribute("avgPSR", roundToTwoDecimalPlaces(industryDto.getAvgPSR()));
        model.addAttribute("avgPBR", roundToTwoDecimalPlaces(industryDto.getAvgPBR()));
        model.addAttribute("avgEV_EBITDA", roundToTwoDecimalPlaces(industryDto.getAvgEV_EBITDA()));

        model.addAttribute("nasdaq100", nasdaq100Service.findByTicker(ticker));
        model.addAttribute("company", firstDto);
        // 숫자를 포맷팅하여 세 자리마다 쉼표 추가
        model.addAttribute("MarketCap", formatNumber(firstDto.getMarket_cap()));
        model.addAttribute("Fluc", firstDto.getFluc());
        model.addAttribute("ClosePrice", firstDto.getClose_price());
        model.addAttribute("edgar", edgarReportsService.getOneEdgarInfo(ticker));

        model.addAttribute("userName", user.getUsername());

        return "/user/details";

    }

    @GetMapping("/search")
    public String searchTicker(@RequestParam String ticker) throws Exception{
        String recent_date = dailyUpdateService.getMostRecentDate();
        String url = String.format("/user/v1/nasdaq/details?ticker=%s&dailydate=%s", ticker, recent_date);
        return "redirect:" + url;
    }


    


    public static double roundToTwoDecimalPlaces(double num) {
        // 소수 둘째 자리까지 확장하여 반올림
        double roundedNum = Math.round(num * 100.0) / 100.0;
        return roundedNum;
    }

    public static String formatNumber(long number) {
        double result;
        String unit;

        if (number >= 1_000_000_000_000L) {
            result = number / 1_000_000_000_000.0;
            unit = "조";
        } else if (number >= 1_000_000_000L) {
            result = number / 1_000_000_000.0;
            unit = "억";
        } else if (number >= 1_000_000L) {
            result = number / 1_000_000.0;
            unit = "백만";
        } else {
            result = number;
            unit = "";
        }

        return String.format("%.1f%s", result, unit);
    }
}

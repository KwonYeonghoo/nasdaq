package com.example.nasdaq.service;

import com.example.nasdaq.model.DTO.NetworkDto;

public interface NetworkService {
    public NetworkDto getOneNetwork(String center, String dailydate);
}

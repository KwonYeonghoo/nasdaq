package com.example.nasdaq.model.DTO;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.ToString;

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
@ToString
public class NetworkDto {
    private String dailydate;
    private String center;

    private String ind1;
    private float corr1;

    private String ind2;
    private float corr2;
    
    private String ind3;
    private float corr3;

    private String ind4;
    private float corr4;

    private String ind5;
    private float corr5;
}


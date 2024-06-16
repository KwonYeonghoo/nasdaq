package com.example.nasdaq.model.Entity;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.ToString;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@ToString
@Entity(name = "DailyUpdateEntity")
@Table(name = "daily_update")
// @IdClass(dailyUpdatesPK.class)
public class DailyUpdateEntity {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank
    private String dailydate;

    @NotBlank
    private String ticker;

    @NotBlank
    private String name;

    private String industry;

    private String news_summary;

    private Long market_cap;

    private double per;

    private double psr;

    private double pbr;

    private double ev_ebitda;

    private double fluc;

    private double close_price;
}
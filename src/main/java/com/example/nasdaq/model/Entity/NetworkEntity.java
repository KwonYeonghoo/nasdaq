package com.example.nasdaq.model.Entity;

import jakarta.persistence.EmbeddedId;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
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
@Entity(name = "Network Entity")
@Table(name = "network")
public class NetworkEntity {
    
    @EmbeddedId
    private NetworkPK networkPK;
    
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

const ticker2 = document.getElementById('ticker').textContent;
const industry2 = document.getElementById('industry').textContent;

Promise.all([
    fetch(`/api/v1/nasdaq/ratios?ticker=${ticker2}`).then(response => response.json()),
    fetch(`/api/v1/nasdaq/industry?industry=${industry2}`).then(response => response.json())
])
.then(([ratioData, industryData]) => {
    // ratioData와 industryData의 형식에 맞게 변환
    const processedRatioData = [
        ratioData.per,
        ratioData.pbr,
        ratioData.ev_ebitda
    ];

    const processedIndustryData = [
        industryData.avgPER,
        industryData.avgPBR,
        industryData.avgEV_EBITDA
    ];

    // Highcharts 차트 생성
    Highcharts.chart('industry2', {
        chart: {
            type: 'column'
        },
        title: {
            text: `${ticker2} vs ${industry2}`,
            align: 'left'
        },
        subtitle: {
            text: 'Source: <a target="_blank" href="https://www.indexmundi.com/agriculture/?commodity=corn">indexmundi</a>',
            align: 'left'
        },
        xAxis: {
            categories: ['PER', 'PBR', 'EV/EBITDA'],
            crosshair: true,
            accessibility: {
                description: 'Ratios'
            }
        },
        yAxis: {
            min: 0,
            title: {
                text: 'Value'
            }
        },
        tooltip: {
            valueSuffix: ''
        },
        plotOptions: {
            column: {
                pointPadding: 0.2,
                borderWidth: 0
            }
        },
        series: [
            {
                name: ticker2,
                data: processedRatioData
            },
            {
                name: industry2,
                data: processedIndustryData
            }
        ]
    });
})
.catch(error => console.error('Error fetching data:', error));
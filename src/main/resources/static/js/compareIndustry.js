document.addEventListener('DOMContentLoaded', (event) => {
    fetch(`/api/v1/nasdaq/industries`)
    .then(response => response.json())
    .then((industryData) => {
        // Extract industry names and corresponding data
        const industryNames = industryData.map(industry => industry.industry);
        const flucValues = industryData.map(industry => industry.avgFluc);
        const perValues = industryData.map(industry => industry.avgPER);

        // Highcharts 차트 생성
        const chart = Highcharts.chart('compareIndustry', {
            chart: {
                zoomType: 'xy'
            },
            title: {
                text: '전날 대비 상승률 Top3 산업군',
                align: 'left'
            },
            xAxis: [{
                categories: industryNames,
                crosshair: true,
                accessibility: {
                    description: 'Top 3 Industry by Fluctuation'
                }
            }],
            yAxis: [{ // Primary yAxis for Market Cap
                labels: {
                    format: '{value}%',
                    style: {
                        color: Highcharts.getOptions().colors[1]
                    }
                },
                title: {
                    text: '등락률 평균 (% 단위)',
                    style: {
                        color: Highcharts.getOptions().colors[1]
                    }
                }
            }, { // Secondary yAxis for PER
                title: {
                    text: 'PER',
                    style: {
                        color: Highcharts.getOptions().colors[0]
                    }
                },
                labels: {
                    format: '{value}',
                    style: {
                        color: Highcharts.getOptions().colors[0]
                    }
                },
                opposite: true
            }],
            tooltip: {
                shared: true
            },
            series: [{
                name: '등락률',
                type: 'column',
                yAxis: 0,
                data: flucValues,
                tooltip: {
                    valueSuffix: ' %'
                },
                events: {
                    click: function(event) {
                        const index = event.point.index;
                        const industryName = industryNames[index];
                        showNetworkChart(industryName);
                    }
                }
            }, {
                name: 'PER',
                type: 'spline',
                yAxis: 1,
                data: perValues,
                tooltip: {
                    valueSuffix: ''
                },
                events: {
                    click: function(event) {
                        const index = event.point.index;
                        const industryName = industryNames[index];
                        showNetworkChart(industryName);
                    }
                }
            }]
        });
    })
    .catch(error => console.error('Error fetching data:', error));
});

function showNetworkChart(industryName) {
    const center = industryName;
    fetch(`/api/v1/nasdaq/network?center=${center}`)
        .then(response => response.json())
        .then(data => {
            // Check if data is an object (single DTO)
            if (typeof data !== 'object' || data === null) {
                console.error('Expected an object but got:', data);
                return;
            }

            // Extract necessary fields from the DTO
            const centerNode = data.center;
            const correlations = [data.corr1, data.corr2, data.corr3, data.corr4, data.corr5];
            const dataArray = [
                [centerNode, data.ind1],
                [centerNode, data.ind2],
                [centerNode, data.ind3],
                [centerNode, data.ind4],
                [centerNode, data.ind5]
            ];

            const nodes = {};
            let i = 0;

            Highcharts.addEvent(
                Highcharts.Series,
                'afterSetOptions',
                function (e) {
                    const colors = Highcharts.getOptions().colors;
                    if (
                        this instanceof Highcharts.Series.types.networkgraph &&
                        e.options.id === 'language-tree'
                    ) {
                        dataArray.forEach(function (link, index) {
                            const correlation = correlations[index];
                            const nodeRadius = correlation * 50;
                            console.log(nodeRadius);

                            if (link[0] === centerNode) {
                                nodes[centerNode] = {
                                    id: centerNode,
                                    marker: {
                                        radius: 54
                                    }
                                };
                                nodes[link[1]] = {
                                    id: link[1],
                                    marker: {
                                        radius: nodeRadius
                                    },
                                    color: colors[i++]
                                };
                            } else if (nodes[link[0]] && nodes[link[0]].color) {
                                nodes[link[1]] = {
                                    id: link[1],
                                    color: nodes[link[0]].color,
                                    marker: {
                                        radius: nodeRadius
                                    }
                                };
                            }
                        });

                        e.options.nodes = Object.keys(nodes).map(function (id) {
                            return nodes[id];
                        });
                    }
                }
            );
            // Check if networkContainer already exists
            let networkChart = Highcharts.charts.find(chart => chart.renderTo.id === 'Network');

            // Render network graph or update existing one
            if (networkChart) {
                networkChart.update({
                    series: [{
                        id: 'language-tree',
                        data: dataArray,
                        nodes: Object.values(nodes)
                    }]
                });
            } else {
            Highcharts.chart('Network', {
                chart: {
                    type: 'networkgraph',
                    marginTop: 80
                },
                title: {
                    text: '유관 산업군 top5'
                },
                subtitle: {
                    text: '네트워크 분석'
                },
                plotOptions: {
                    networkgraph: {
                        keys: ['from', 'to'],
                        layoutAlgorithm: {
                            enableSimulation: true,
                            integration: 'verlet',
                            linkLength: 200
                        }
                    }
                },
                series: [{
                    id: 'language-tree',
                    marker: {
                        radius: 13
                    },
                    dataLabels: {
                        enabled: true,
                        textPath: {
                            enabled: false
                        },
                        style: {
                            fontWeight: 'bold',
                            fontSize: 16
                        },
                        align: 'right',
                        verticalAlign: 'middle',
                        linkFormat: '',
                        allowOverlap: true
                    },
                    data: dataArray
                }]
            });
        }
            const modal = document.getElementById('networkModal');
            document.getElementById('Network').style.display = 'block';
            modal.style.display = 'block';
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });

}

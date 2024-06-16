const center = "Semiconductors/Technology";
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
                    dataArray.forEach(function (link) {
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
                                    radius: 32
                                },
                                color: colors[i++]
                            };
                        } else if (nodes[link[0]] && nodes[link[0]].color) {
                            nodes[link[1]] = {
                                id: link[1],
                                color: nodes[link[0]].color
                            };
                        }
                    });

                    e.options.nodes = Object.keys(nodes).map(function (id) {
                        return nodes[id];
                    });
                }
            }
        );

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
                        enabled: true
                    },
                    style: {
                        fontWeight: 'bold'
                    },
                    linkFormat: '',
                    allowOverlap: true
                },
                data: dataArray
            }]
        });
    })
    .catch(error => {
        console.error('Error fetching data:', error);
    });

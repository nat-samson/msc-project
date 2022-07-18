/**
 * Updates the text displayed in multiple UI boxes with data from a single AJAX request.
 * @param {Element[]} boxes - An array of HTML Elements.
 * @param {String} url - A String representing a URL to use for the GET request.
 */
function updateDataBoxes(boxes, url) {
    $.ajax({
        method: "GET",
        dataType: "json",
        url: url,
        success: (data) => {
            // update all the data boxes
            const dataArray = Object.values(data)
            for (let i = 0; i < dataArray.length; i++) {
                boxes[i].lastElementChild.innerText = dataArray[i]
            }
        },
        error: (error_data) => {
            console.log(error_data)
        }
    })
}

function updateChart(chart, url) {
    $.ajax({
        method: "GET",
        dataType: "json",
        url: url,
        success: (chartData) => {
            chart['data'] = chartData;
            chart.update();
        },
        error: (error_data) => {
            console.log("Failed to fetch chart data.")
            console.log(error_data)
        }
    })
}

function updateCharts(charts, url) {
    $.ajax({
        method: "GET",
        dataType: "json",
        url: url,
        success: (chartsData) => {
            // update the charts
            const dataArray = Object.values(chartsData);
            for (let i = 0; i < dataArray.length; i++) {
                charts[i]['data'] = dataArray[i]
                charts[i].update();
            }
        },
        error: (error_data) => {
            console.log("Failed to fetch chart data.")
            console.log(error_data)
        }
    })
}

function getChartSettings(chartType){
    let chartSettings =  {
        type: chartType,
        options: {}
    };
    // only show the legend for pie charts
    if(chartType!=='pie'){
        chartSettings.options['plugins'] = {
            legend: {
                display: false,
            },
        };
    }
    return chartSettings;
}
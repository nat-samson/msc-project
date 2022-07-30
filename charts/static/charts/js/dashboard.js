/**
 * @file Common data-visualisation helper functions for use by dashboard and progress HTML templates.
 * @author Nathaniel Samson
 */

/**
 * Asynchronously retrieves data from the server and hands it to an Updater function to display.
 *
 * @param {(Chart[]|Chart|Element[])} target - An HTML element (or array of HTML elements) to be updated with new data.
 * @param {String} url - A String representing a URL to use for the GET request.
 * @param {Function} updaterFunc - A Function that updates the target with the retrieved data.
 */
function updateData(target, url, updaterFunc) {
    $.ajax({
        method: "GET",
        dataType: "json",
        url: url,
        success: (data) => {
            updaterFunc(target, data);
        },
        failure: (error) => {
            console.log("Failed to retrieve data from server.", error)
        }
    })
}

/**
 * Updates the innerText displayed in the 'box' elements in the Dashboard UI.
 * @param {Element[]} boxes - An array of HTML Elements to be updated with new data.
 * @param data - The raw data retrieved by updateData's asynchronous request.
 */
function boxesUpdater(boxes, data) {
            // update all the boxes
            const dataArray = Object.values(data);
            for (let i = 0; i < dataArray.length; i++) {
                boxes[i].lastElementChild.innerText = dataArray[i];
            }
}

/**
 * Updates the chart with data received by updateData().
 * @param {Chart} chart - A Chart object to be updated with new data.
 * @param data - The raw data retrieved by updateData's asynchronous request.
 */
function chartUpdater(chart, data) {
            // update the given chart
            chart['data'] = data;
            chart.update();
}

/**
 * Updates each chart in the given array with data received by updateData().
 * @param {Chart[]} chartsArray - An array of Chart objects to be updated with new data.
 * @param data - The raw data retrieved by updateData's asynchronous request.
 */
function chartsUpdater(chartsArray, data) {
    // update each chart in the array
    const dataArray = Object.values(data);
    for (let i = 0; i < dataArray.length; i++) {
        chartsArray[i]['data'] = dataArray[i];
        chartsArray[i].update();
    }
}

/**
 * Clears the rows in the given table and replaces with data received by updateData().
 * @param {HTMLTableElement} tableBody - A reference to a <tbody> HTML Element.
 * @param tableData - The raw data retrieved by updateData's asynchronous request.
 */
function tableUpdater(tableBody, tableData) {
    // clear existing table rows
    while (tableBody.firstChild) {
        tableBody.removeChild(tableBody.firstChild);
    }

    // add new rows (and cells)
    tableData.forEach(row => {
        let newRow = tableBody.insertRow(-1);

        row.forEach(cell => {
            let newCell = newRow.insertCell(-1);
            newCell.innerText = cell;
        })
    })
}

/**
 * Returns the template of common Chart settings for building the Chart objects.
 * @param {String} chartType - A String representing the type of Chart to be created.
 * @returns {{options: {}, type: {String}}} - An Object representing the settings for a Chart.
 */
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
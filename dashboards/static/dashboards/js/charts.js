// General function to handle fetching data and plotting the chart
function handleChartClick(endpoint, chartID, chartLabel, chartContainerID) {
  // This will use the chartContainerID to extract the value seleced from the pack/pick name dropdown and time period
  // It will use the endpoint to get the labels and values to populate the chart
  // ChartID is then used to populate the chart in plotChart

  const chartContainer = document.getElementById(chartContainerID);
  const pack = chartContainer.querySelector(".pack-select").value;
  const timePeriod = chartContainer.querySelector(".time-filter").value; 

  // Check if a pack is selected
  if (!pack) {
    alert("Please select a pack.");
    return;
  }

  // Send the POST request
  console.log("csrfToken: ", csrfToken);
  fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken, // Include CSRF token for security
    },
    body: JSON.stringify({ pack: pack, time_filter: timePeriod }), // Send selected values
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json(); // Parse JSON data
    })
    .then((data) => {
      // Call a function to plot the chart using the returned data
      plotChart(data.labels, data.counts, chartID, chartLabel);
      
      let widgetContainer = chartContainer.nextElementSibling
      console.log("widget container: ", widgetContainer)
      console.log("pack count: ", data.total_packs_count);
      widgetContainer.querySelector('.pack-count strong').textContent = data.total_packs_count;
      widgetContainer.querySelector('.promo-count strong').textContent = data.promo_count;
      widgetContainer.querySelector('.totw-count strong').textContent = data.totw_count;
      widgetContainer.querySelector('.hero-count strong').textContent = data.hero_count;
      widgetContainer.querySelector('.icon-count strong').textContent = data.icon_count;


    })
    .catch((error) => {
      console.error("Error fetching data:", error);
    });
}

// Event listener for Pack Chart
document.getElementById("pack-chart-button").addEventListener("click", function () {
  handleChartClick("api/create-distribution-rating-chart/", "pack-ratings-chart", "Pack Ratings", "pack-chart-container");
});

// Event listener for Pick Chart
document.getElementById("pick-chart-button").addEventListener("click", function () {
  handleChartClick("api/create-distribution-rating-chart/", "pick-ratings-chart", "Pick Ratings", "pick-chart-container");
});

// Function to plot the chart
function plotChart(labels, counts, chartID, chartLabel) {
  console.log("Attempting to plot chart with chartID:", chartID);
  console.log("labels: ", labels);
  console.log("counts: ", counts);

  const ctx = document.getElementById(chartID).getContext("2d");

  // Ensure each chart has its own unique instance stored in the window object
  if (!window.charts) {
    window.charts = {}; // Initialize an empty object to store chart instances
  }

  // Check if a chart instance already exists for this chartID, and destroy it if so
  if (window.charts[chartID]) {
    window.charts[chartID].destroy();
  }

  // Create a new chart and store the instance in the window.charts object
  window.charts[chartID] = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: chartLabel,
          data: counts,
          backgroundColor: "rgba(75, 192, 192, 0.2)",
          borderColor: "rgba(75, 192, 192, 1)",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });
}
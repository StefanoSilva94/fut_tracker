document.getElementById("plot-button").addEventListener("click", function () {
  const pack = document.getElementById("pack-select").value;
  const timePeriod = document.getElementById("time-filter").value;

  console.log("timePeriod", timePeriod);
  
  // Check if a pack is selected
  if (!pack) {
    alert("Please select a pack.");
    return;
  }

  // Send the POST request
  fetch("api/get_pack_data/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken, // Include CSRF token for security
    },
    body: JSON.stringify({ pack: pack, time: timePeriod }), // Send selected values
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json(); // Parse JSON data
    })
    .then((data) => {
      // Call a function to plot the chart using the returned data
      plotChart(data.labels, data.counts);
    })
    .catch((error) => {
      console.error("Error fetching data:", error);
    });
});

// Function to plot the chart
function plotChart(labels, counts) {
    console.log("attempting to plot chart")
    console.log("labels: ", labels)
    console.log("counts: ", counts);

  const ctx = document.getElementById("ratingsChart").getContext("2d");
  if (window.myChart) {
    window.myChart.destroy(); // Destroy existing chart instance if it exists
  }

  window.myChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Data",
          data: counts,
          backgroundColor: "rgba(75, 192, 192, 0.2)",
          borderColor: "rgba(75, 192, 192, 1)",
          borderWidth: 1,
        },
      ],
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });
}

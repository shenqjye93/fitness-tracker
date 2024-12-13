document.addEventListener("DOMContentLoaded", () => {
    const totalExercisesElem = document.getElementById("totalExercises");
    const totalWeightElem = document.getElementById("totalWeight");
    const latestExercisesElem = document.getElementById("latestExercises");
    const exerciseFilterElem = document.getElementById("filter");

    // Fetch all exercises and update the dashboard
    const fetchDashboardData = async () => {
        try {
            const response = await fetch("/exercises");
            const exercises = await response.json();

            // Populate filter dropdown
            populateExerciseFilter(exercises);

            // Render dashboard based on current filter
            updateDashboard(exercises, exerciseFilterElem.value);

        } catch (error) {
            console.error("Error fetching dashboard data:", error);
        }
    };

    // Populate the dropdown for exercise selection
    const populateExerciseFilter = (exercises) => {
        const exerciseNames = [...new Set(Object.values(exercises).map(ex => ex.name))];
        exerciseFilterElem.innerHTML = `<option value="all">All Exercises</option>`;
        exerciseNames.forEach(name => {
            const option = document.createElement("option");
            option.value = name;
            option.textContent = name;
            exerciseFilterElem.appendChild(option);
        });
    };



    // Update the dashboard
    const updateDashboard = (exercises, selectedExercise) => {
        // Fetch all exercises (or use cached data if available)

        // Filter exercises based on the selection
        const filteredExercises = selectedExercise === "all" ? exercises :
            Object.values(exercises).filter(ex => ex.name === selectedExercise);

        // Update total exercises
        const totalExercises = Object.keys(filteredExercises).length;
        totalExercisesElem.textContent = totalExercises;

        // Calculate total weight lifted
        const totalWeight = Object.values(filteredExercises).reduce((sum, exercise) => sum + exercise.weight, 0);
        totalWeightElem.textContent = totalWeight.toFixed(2);

        // Display latest exercises
        renderLatestExercises(filteredExercises);

        // Update the graph
        renderWeightGraph(filteredExercises);
    };




    // Render the latest exercises
    const renderLatestExercises = (exercises) => {
        latestExercisesElem.innerHTML = "";

        const exerciseArray = Object.values(exercises);
        const latest = exerciseArray.slice(-10).reverse(); // Show the last 5 exercises

        latest.forEach((exercise) => {
            const li = document.createElement("li");
            li.textContent = `${exercise.name} - ${exercise.type} - ${exercise.weight} kg`;
            latestExercisesElem.appendChild(li);
        });
    };

    exerciseFilterElem.addEventListener("change", async () => {
        try {
            const response = await fetch("/exercises");
            const exercises = await response.json();
            updateDashboard(exercises, exerciseFilterElem.value);
        } catch (error) {
            console.error("Error fetching exercises on filter change:", error);
        }
    });

    fetchDashboardData();

});

let weightChart; // To hold the Chart.js instance

const renderWeightGraph = (exercises) => {
    const ctx = document.getElementById("weightChart").getContext("2d");

    // Prepare data for the graph
    const dates = Object.values(exercises).map(ex => {
        return new Date(parseInt(ex.id)).toISOString().split("T")[0];
    });
    const weights = Object.values(exercises).map(ex => ex.weight);

    const limit = 10;
    const limitedDates = dates.slice(-limit);

    // Debug logs
    console.log("Dates for graph:", dates);
    console.log("Weights for graph:", weights);

    // Destroy the previous chart if it exists
    if (weightChart) {
        weightChart.destroy();
    }

    // Create a new chart
    weightChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: limitedDates, // Dates on the x-axis
            datasets: [{
                label: "Weight Lifted (kg)",
                data: weights,
                borderColor: "rgba(75, 192, 192, 1)",
                backgroundColor: "rgba(75, 192, 192, 0.2)",
                borderWidth: 2,
            }],
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: true },
            },
            scales: {
                x: { title: { display: true, text: "Date" } },
                y: { title: { display: true, text: "Weight (kg)" } },
            },
        },
    });
};


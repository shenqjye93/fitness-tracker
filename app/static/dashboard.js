function toggleSidebar() {
	const menu = document.querySelector(".menu-toggle");
	const icon = document.querySelector(".toggle-sidebar");

	menu.classList.toggle("open");
	icon.classList.toggle("open");
}

document.addEventListener("DOMContentLoaded", () => {
	let allExercises = {};
	let exerciseChart;

	const summaryList = document.getElementById("data-info");
	const exerciseFilter = document.getElementById("exercise-filter");
	const links = document.querySelectorAll(".navbar a");
	const currentPath = window.location.pathname;

	links.forEach((link) => {
		if (link.getAttribute("href") === currentPath) {
			link.classList.add("active");
		} else {
			link.classList.remove("active");
		}
	});

	// Fetch and process data
	async function fetchData() {
		try {
			const [exercisesResponse, metricsResponse] = await Promise.all([
				fetch("/exercises"),
				fetch("/metrics"),
			]);

			const exercises = await exercisesResponse.json();
			const metrics = await metricsResponse.json();

			allExercises = exercises;
			createExerciseChart(exercises);
			createBPChart(metrics);
			createGlucoseChart(metrics);
			updateStreak();
			createDynamicDropdown(exercises);
			renderSummary(exercises);
		} catch (error) {
			console.error("Error fetching data:", error);
		}
	}

	function createExercisePb(exercises, filterName = null) {
		const prInfo = document.getElementById("pr-info");
		const exerciseData = processExerciseData(exercises, filterName);
		console.log(exerciseData);

		prInfo.innerHTML = "";
		prWeight = Math.max(...exerciseData.weights);

		const ul = document.createElement("ul");
		ul.innerHTML = `
            <small>PR: ${filterName}</small>
            <br>
            <strong>${prWeight} kg</strong>`;

		prInfo.appendChild(ul);
	}

	function createExerciseChart(exercises, filterName = null) {
		const ctx = document.getElementById("exercise-chart").getContext("2d");
		const exerciseData = processExerciseData(exercises, filterName);

		if (exerciseChart) {
			exerciseChart.destroy();
		}

		exerciseChart = new Chart(ctx, {
			type: "line",
			data: {
				labels: exerciseData.labels,
				datasets: [
					{
						label: "Exercise Weights",
						data: exerciseData.weights,
						fill: true,
						backgroundColor: "rgba(156, 132, 251, 0.2)",
						borderColor: "rgba(156, 132, 251, 1)",
						borderWidth: 3,
						tension: 0.4,
					},
				],
			},
			options: {
				responsive: true,
				plugins: {
					legend: false,
					tooltip: {
						callbacks: {
							label: function (exerciseData) {
								return `${exerciseData.raw} kg`;
							},
						},
					},
				},

				scales: {
					y: {
						beginAtZero: true,
						title: {
							display: false,
							text: "Weight (kg)",
							color: "#666666",
						},
						grid: {
							color: "#333333",
						},
						ticks: {
							color: "#666666",
							font: {
								weight: "bold",
							},
						},
						border: {
							color: "transparent",
						},
					},
					x: {
						title: {
							color: "#666666",
						},
						border: {
							color: "transparent",
						},
						grid: {
							color: "transparent",
						},
						ticks: {
							color: "#666666",
							font: {
								weight: "bold",
							},
						},
					},
				},
			},
		});
	}

	function processExerciseData(exercises, filterName = null) {
		const labels = [];
		const names = [];
		const weights = [];

		for (const id in exercises) {
			const exercise = exercises[id];
			if (
				exercise.category === "exercise" &&
				(filterName === null || exercise.name === filterName)
			) {
				labels.push(getRelativeDate(id));
				weights.push(exercise.weight);
				names.push(exercise.name);
			}
		}

		return { labels, weights, names };
	}

	function createBPChart(metrics) {
		const ctx = document.getElementById("bp-chart").getContext("2d");
		const bpData = processBPData(metrics);

		new Chart(ctx, {
			type: "bar",
			data: {
				labels: bpData.labels,
				datasets: [
					{
						label: "Systolic",
						data: bpData.systolic,
						borderColor: "rgba(32, 171, 217, 1)",
						backgroundColor: "rgba(32, 171, 217, 1)",
					},
					{
						label: "Diasystolic",
						data: bpData.diasystolic,
						borderColor: "rgba(59, 109, 194, 0.8)",
						backgroundColor: "rgba(59, 109, 194, 0.8)",
					},
				],
			},
			options: {
				responsive: true,
				scales: {
					y: {
						title: {
							display: false,
							text: "Blood Pressure (mmHg)",
							color: "#666666",
						},
						grid: {
							color: "#333333",
						},
						ticks: {
							color: "#666666",
							font: {
								weight: "bold",
							},
						},
						border: {
							color: "transparent",
						},
					},
					x: {
						grid: {
							color: "transparent",
						},
						ticks: {
							color: "#666666",
							font: {
								weight: "bold",
							},
						},
						border: {
							color: "transparent",
						},
					},
				},
			},
		});
	}

	function processBPData(metrics) {
		const labels = [];
		const systolic = [];
		const diasystolic = [];

		for (const id in metrics) {
			const metric = metrics[id];
			if (metric.type === "bp") {
				labels.push(getRelativeDate(id));
				systolic.push(metric.systolic);
				diasystolic.push(metric.diasystolic);
			}
		}

		return { labels, systolic, diasystolic };
	}

	function createGlucoseChart(metrics) {
		const ctx = document.getElementById("glucose-chart").getContext("2d");
		const glucoseData = processGlucoseData(metrics);

		new Chart(ctx, {
			type: "bar",
			data: {
				labels: glucoseData.labels,
				datasets: [
					{
						label: "Glucose Levels",
						data: glucoseData.levels,
						borderColor: "rgb(116, 82, 255)",
						backgroundColor: "rgba(156, 132, 251, 0.8)",
					},
				],
			},
			options: {
				plugins: {
					legend: false,
				},
				responsive: true,
				scales: {
					y: {
						title: {
							display: false,
							text: "Glucose (mmol/L)",
							color: "#666666",
						},
						grid: {
							color: "#333333",
						},
						ticks: {
							color: "#666666",
							font: {
								weight: "bold",
							},
						},
						border: {
							color: "transparent",
						},
					},
					x: {
						grid: {
							color: "transparent",
						},
						ticks: {
							color: "#666666",
							font: {
								weight: "bold",
							},
						},
						border: {
							color: "transparent",
						},
					},
				},
			},
		});
	}

	function processGlucoseData(metrics) {
		const labels = [];
		const levels = [];

		for (const id in metrics) {
			const metric = metrics[id];
			if (metric.type === "glucose") {
				labels.push(getRelativeDate(id));
				levels.push(metric.level);
			}
		}

		return { labels, levels };
	}

	function createDynamicDropdown(exercises) {
		const exerciseDropdownContainer =
			document.getElementById("exercise-filter");
		const uniqueExerciseTypes = new Set();

		// Clear existing options
		exerciseDropdownContainer.innerHTML =
			'<option value="">Filter Exercises</option>';

		for (const id in exercises) {
			const exercise = exercises[id];
			if (exercise.category === "exercise") {
				uniqueExerciseTypes.add(exercise.name);
			}
		}

		// Add players to select
		uniqueExerciseTypes.forEach((name) => {
			const option = document.createElement("option");
			option.value = name;
			option.textContent = `${name}`;

			exerciseFilter.addEventListener("change", () => {
				const selectedName = event.target.value;
				filterExercises(selectedName);
			});

			exerciseDropdownContainer.appendChild(option);
		});
	}

	function filterExercises(name) {
		createExerciseChart(allExercises, name);
		createExercisePb(allExercises, name);
	}

	function getRelativeDate(id) {
		const date = new Date(parseInt(id));
		const today = new Date();
		const diffTime = today - date;
		const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

		// Set both dates to midnight for comparison
		const dateDay = new Date(date.setHours(0, 0, 0, 0));
		const todayDay = new Date(today.setHours(0, 0, 0, 0));

		// Get day names
		const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
		const months = [
			"Jan",
			"Feb",
			"Mar",
			"Apr",
			"May",
			"Jun",
			"Jul",
			"Aug",
			"Sep",
			"Oct",
			"Nov",
			"Dec",
		];

		if (dateDay.getTime() === todayDay.getTime()) {
			return "Today";
		} else if (diffDays === 1) {
			return "Yesterday";
		} else if (diffDays < 7) {
			return days[date.getDay()];
		} else if (diffDays > 28) {
			return months[date.getMonth()];
		} else {
			return date.toLocaleDateString();
		}
	}

	function updateStreak() {
		// Get all exercises
		fetch("/exercises")
			.then((response) => response.json())
			.then((exercises) => {
				// Create a map of dates when exercises were logged
				const exerciseDates = new Set();

				// Process all exercise dates
				for (const id in exercises) {
					const date = new Date(parseInt(id));
					exerciseDates.add(date.toDateString());
				}

				// Get today's date
				const today = new Date().toDateString();

				// Calculate current streak
				let currentStreak = 0;
				let date = new Date();

				// Count backwards from today until we find a day without exercise
				while (
					exerciseDates.has(date.toDateString()) ||
					date.toDateString() === today
				) {
					if (exerciseDates.has(date.toDateString())) {
						currentStreak++;
					}
					date.setDate(date.getDate() - 1);
				}

				// Update streak counter display
				const streakCounter = document.querySelector(".streak-counter");
				streakCounter.innerHTML = `
                    <div class="streak-calendar">
                        <strong>${currentStreak}</strong>
                        <br>
                        <small>Days</small>
                    </div>
                `;
			});
	}

	const renderSummary = (exercises, limit = 6) => {
		summaryList.innerHTML = "";

		const exerciseArray = Object.entries(exercises)
			.filter(([_, exercise]) => exercise.category === "exercise")
			.sort(([idA], [idB]) => idB - idA)
			.slice(0, limit);

		exerciseArray.forEach(([id, exercise]) => {
			const tr = document.createElement("tr");
			tr.innerHTML = `
                <td>${exercise.name}</td>
                <td>${exercise.type}</td>
                <td>${getRelativeDate(id)}</td>
            `;
			summaryList.appendChild(tr);
		});
	};


	// Initial data fetch
	fetchData();
});

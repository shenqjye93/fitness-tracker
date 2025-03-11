import userManagement from "./user-manager-objects.js";

document.addEventListener("DOMContentLoaded", async () => {
	let allExercises = {};
	let exerciseChart;

	const summaryList = document.getElementById("data-info");
	const exerciseFilter = document.getElementById("exercise-filter");
	const links = document.querySelectorAll(".navbar a");
	const currentPath = window.location.pathname;
	const isLoggedIn = await userManagement.isAuthenticated();

	if (!isLoggedIn) {
		window.location.href = "/";
	}
	console.log("Welcome,", userManagement.user.username, isLoggedIn);

	await userManagement.getCurrentUser();

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

		const weights = exerciseData.datasets.flatMap((dataset) =>
			dataset.data.map((point) => point.y)
		);
		console.log(weights);

		prInfo.innerHTML = "";
		const prWeight = Math.max(...weights);

		const ul = document.createElement("ul");
		ul.innerHTML = `
            <small>PR: ${filterName}</small>
            <br>
            <strong>${prWeight} kg</strong>`;

		prInfo.appendChild(ul);
	}

	function createExerciseChart(exercises, filterName = null) {
		const ctx = document.getElementById("exercise-chart").getContext("2d");
		const { datasets } = processExerciseData(exercises, filterName);

		if (exerciseChart) exerciseChart.destroy();

		exerciseChart = new Chart(ctx, {
			type: "line",
			data: { datasets: datasets },
			options: {
				responsive: true,
				plugins: {
					legend: { display: false }, // Show legend to toggle exercises
					tooltip: {
						callbacks: {
							label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y} kg`,
						},
					},
				},
				scales: {
					x: {
						type: "linear", // Use a linear scale instead of 'time'
						ticks: {
							callback: function (value) {
								// Format the tick as a date string
								return new Date(value).toLocaleDateString();
							},
						},
					},
					y: {
						beginAtZero: false,
						ticks: { color: "#666666" },
						grid: { color: "#333333" },
					},
				},
			},
		});
	}
	// function createExerciseChart(exercises, filterName = null) {
	// 	const ctx = document.getElementById("exercise-chart").getContext("2d");
	// 	const exerciseData = processExerciseData(exercises, filterName);

	// 	if (exerciseChart) {
	// 		exerciseChart.destroy();
	// 	}

	// 	exerciseChart = new Chart(ctx, {
	// 		type: "line",
	// 		data: {
	// 			labels: exerciseData.labels,
	// 			datasets: [
	// 				{
	// 					label: "Exercise Weights",
	// 					data: exerciseData.weights,
	// 					fill: true,
	// 					backgroundColor: "rgba(156, 132, 251, 0.2)",
	// 					borderColor: "rgba(156, 132, 251, 1)",
	// 					borderWidth: 3,
	// 					tension: 0.4,
	// 				},
	// 			],
	// 		},
	// 		options: {
	// 			responsive: true,
	// 			plugins: {
	// 				legend: false,
	// 				tooltip: {
	// 					callbacks: {
	// 						label: function (exerciseData) {
	// 							return `${exerciseData.raw} kg`;
	// 						},
	// 					},
	// 				},
	// 			},

	// 			scales: {
	// 				y: {
	// 					beginAtZero: true,
	// 					title: {
	// 						display: false,
	// 						text: "Weight (kg)",
	// 						color: "#666666",
	// 					},
	// 					grid: {
	// 						color: "#333333",
	// 					},
	// 					ticks: {
	// 						color: "#666666",
	// 						font: {
	// 							weight: "bold",
	// 						},
	// 					},
	// 					border: {
	// 						color: "transparent",
	// 					},
	// 				},
	// 				x: {
	// 					title: {
	// 						color: "#666666",
	// 					},
	// 					border: {
	// 						color: "transparent",
	// 					},
	// 					grid: {
	// 						color: "transparent",
	// 					},
	// 					ticks: {
	// 						color: "#666666",
	// 						font: {
	// 							weight: "bold",
	// 						},
	// 					},
	// 				},
	// 			},
	// 		},
	// 	});
	// }

	function processExerciseData(exercisesObj, filterName = null) {
		//Object.entries converts object data into array [key:values] pair
		//in my example would be [id(can be used as timestamp): exercises]
		const entries = Object.entries(exercisesObj);

		const exercisesMap = new Map();
		entries.forEach(([timestamp, exercise]) => {
			const { name, weight } = exercise;

			if (filterName && name !== filterName) return;

			const exerciseDate = new Date(Number(timestamp));

			if (!exercisesMap.has(name)) {
				exercisesMap.set(name, []);
			}

			exercisesMap.get(name).push({
				x: exerciseDate,
				y: weight,
			});
		});

		// Cannot use forEach because my data is not an Array
		// exercises.forEach(({name, date, weight}) => {
		// 	if (filterName && name !== filterName) return;
		// 	if (!exercisesMap.has(name)) {
		// 		exercisesMap.set(name, []);
		// 	}
		const generateColors = generateChartColors(exercisesMap.size);

		// Convert to datasets array
		const datasets = Array.from(exercisesMap.entries()).map(
			([name, data], idx) => {
				const color = generateColors[idx % generateColors.length];
				return {
					label: name,
					data: data.sort((a, b) => a.x - b.x), // Sort by date
					borderColor: color.rgb,
					backgroundColor: color.rgba,
					fill: true,
					borderWidth: 1,
					tension: 0.069,
				};
			}
		);
		return { datasets };
	}

	function adjustLightness(hex, percent) {
		hex = hex.replace(/^#/, "").trim();

		// Expand shorthand if needed (e.g., "abc" -> "aabbcc")
		if (hex.length === 3) {
			hex = hex
				.split("")
				.map((ch) => ch + ch)
				.join("");
		}

		const num = parseInt(hex, 16);
		let r = (num >> 16) & 0xff;
		let g = (num >> 8) & 0xff;
		let b = num & 0xff;

		r = Math.min(255, Math.max(0, r + Math.round(255 * (percent / 100))));
		g = Math.min(255, Math.max(0, g + Math.round(255 * (percent / 100))));
		b = Math.min(255, Math.max(0, b + Math.round(255 * (percent / 100))));

		return (
			"#" +
			[r, g, b]
				.map((x) => x.toString(16).padStart(2, "0"))
				.join("")
				.toUpperCase()
		);
	}

	function hexToRgb(hex) {
		hex = hex.replace(/^#/, "");
		if (hex.length === 3) {
			hex = hex
				.split("")
				.map((ch) => ch + ch)
				.join("");
		}
		const bigint = parseInt(hex, 16);
		const r = (bigint >> 16) & 255;
		const g = (bigint >> 8) & 255;
		const b = bigint & 255;

		return `rgb(${r}, ${g}, ${b})`;
	}

	function hexToRgba(hex, alpha) {
		hex = hex.replace(/^#/, "");
		if (hex.length === 3) {
			hex = hex
				.split("")
				.map((ch) => ch + ch)
				.join("");
		}
		const bigint = parseInt(hex, 16);
		const r = (bigint >> 16) & 255;
		const g = (bigint >> 8) & 255;
		const b = bigint & 255;

		return `rgba(${r}, ${g}, ${b}, ${alpha})`;
	}

	function generateChartColors(count, alpha = 0.2) {
		// Base palette in hex.
		const baseColors = [
			"#1779e9",
			"#4a9eff",
			"#7452FF", // equivalent to rgb(116,82,255)
			"#9c84FB", // equivalent to rgb(156,132,251)
		];

		const colorObjects = [];
		const baseCount = baseColors.length;

		// Calculate how many variants per base color are needed.
		const variantsPerBase = Math.ceil(count / baseCount);

		baseColors.forEach((base) => {
			if (variantsPerBase === 1) {
				// If only one variant is needed, use the base color.
				colorObjects.push({
					rgb: hexToRgb(base),
					rgba: hexToRgba(base, alpha),
				});
			} else {
				// Generate variants by adjusting lightness.
				// Variation range: from -10% to +10%.
				for (let i = 0; i < variantsPerBase; i++) {
					const variationStep = 20 / (variantsPerBase - 1); // total range 20%
					const percentAdjustment = -10 + i * variationStep; // from -10% to +10%
					const variantHex = adjustLightness(base, percentAdjustment);
					colorObjects.push({
						rgb: hexToRgb(variantHex),
						rgba: hexToRgba(variantHex, alpha),
					});
				}
			}
		});

		// Return exactly the number of colors requested.
		return colorObjects.slice(0, count);
	}

	// function processExerciseData(exercises, filterName = null) {
	// 	const labels = [];
	// 	const names = [];
	// 	const weights = [];

	// 	for (const id in exercises) {
	// 		const exercise = exercises[id];
	// 		if (
	// 			exercise.category === "exercise" &&
	// 			(filterName === null || exercise.name === filterName)
	// 		) {
	// 			labels.push(getRelativeDate(id));
	// 			weights.push(exercise.weight);
	// 			names.push(exercise.name);
	// 		}
	// 	}

	// 	return { labels, weights, names };
	// }

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

		uniqueExerciseTypes.forEach((name) => {
			const option = document.createElement("option");
			option.value = name;
			option.textContent = name;
			exerciseDropdownContainer.appendChild(option);
		});

		exerciseFilter.addEventListener("change", (event) => {
			const selectedName = event.target.value;
			filterExercises(selectedName);
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

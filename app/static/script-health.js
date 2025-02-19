import userManagement from "./user-manager-objects.js";

document.addEventListener("DOMContentLoaded", async () => {
	const bpForm = document.getElementById("bp-form");
	const glucoseForm = document.getElementById("glucose-form");
	const bpList = document.getElementById("bp-list");
	const glucoseList = document.getElementById("glucose-list");
	const links = document.querySelectorAll(".navbar a");
	const currentPath = window.location.pathname;
	const isLoggedIn = await userManagement.isAuthenticated();

	if (!isLoggedIn) {
		window.location.href = "/";
	}
	console.log(
		"Welcome,",
		userManagement.user.username,
		userManagement.user.user_id
	);

	links.forEach((link) => {
		if (link.getAttribute("href") === currentPath) {
			link.classList.add("active");
		} else {
			link.classList.remove("active");
		}
	});

	// Fetch and display exercises
	const fetchMetrics = async () => {
		const response = await fetch("/metrics");
		const metrics = await response.json();
		renderMetrics(metrics);
	};

	// Render metric list
	const renderMetrics = (metrics) => {
		bpList.innerHTML = "";
		glucoseList.innerHTML = "";
		for (const id in metrics) {
			const metric = metrics[id];

			if (metric.type === "bp") {
				const li = document.createElement("li");
				const day = getRelativeDate(id);
				li.innerHTML = `
                <div class="record-item">
                    <div class="record-details">
                          <strong>Blood Pressure:</strong> ${metric.systolic}/${metric.diasystolic} mmHg
                          <br>
                          <strong>Pulse:</strong> ${metric.pulse} bpm 
                          <br>
                          <small>${day}, 2:30 PM</small>
                    </div>
                    <div class="record-actions">
                        <button class="btn-edit" onclick="editBp('${id}')">Edit</button>
                        <button class="btn-delete" onclick="deleteMetric('${id}')">Delete</button>
                    </div>
                </div>
                `;
				console.log(bpList);
				bpList.appendChild(li);
			}

			if (metric.type === "glucose") {
				const li = document.createElement("li");
				const day = getRelativeDate(id);
				li.innerHTML = `
                <div class="record-item">
                    <div class="record-details">
                          <strong> Glucose:</strong> ${metric.level} mmol/L
                          <br> 
                          <small>${day}, 2:30 PM</small>
                    </div>
                    <div class="record-actions">
                        <button class="btn-edit" onclick="editGlucose('${id}')">Edit</button>
                        <button class="btn-delete" onclick="deleteMetric('${id}')">Delete</button>
                    </div>
                  `;
				glucoseList.appendChild(li);
			}
		}
	};

	// Add or update metric
	bpForm.addEventListener("submit", async (e) => {
		e.preventDefault();
		const id =
			document.getElementById("metricId").value || Date.now().toString();
		const type = "bp";
		const systolic = document.getElementById("systolic").value;
		const diasystolic = document.getElementById("diasystolic").value;
		const pulse = document.getElementById("pulse").value;
		const user_id = userManagement.user.user_id;

		const method = document.getElementById("metricId").value ? "PUT" : "POST";
		await fetch(`/create-bp/${id}`, {
			method,
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				id: parseInt(id),
				type,
				systolic,
				diasystolic,
				pulse,
				user_id,
			}),
		});

		document.getElementById("bp-form").reset();
		document.getElementById("metricId").value = "";
		fetchMetrics();
	});

	glucoseForm.addEventListener("submit", async (e) => {
		e.preventDefault();
		const id =
			document.getElementById("metricId").value || Date.now().toString();
		const type = "glucose";
		const level = document.getElementById("glucose").value;
		const user_id = userManagement.user.user_id;

		const method = document.getElementById("metricId").value ? "PUT" : "POST";
		await fetch(`/create-glucose/${id}`, {
			method,
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				id: parseInt(id),
				type,
				level,
				user_id,
			}),
		});

		document.getElementById("glucose-form").reset();
		document.getElementById("metricId").value = "";
		fetchMetrics();
	});

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

		if (dateDay.getTime() === todayDay.getTime()) {
			return "Today";
		} else if (diffDays === 1) {
			return "Yesterday";
		} else if (diffDays < 7) {
			return days[date.getDay()];
		} else {
			return date.toLocaleDateString();
		}
	}

	// Edit metric
	window.editBp = async (id) => {
		const response = await fetch(`/get-metrics/${id}`);
		const metric = await response.json();

		document.getElementById("metricId").value = id;
		document.getElementById("systolic").value = metric.systolic;
		document.getElementById("diasystolic").value = metric.diasystolic;
		document.getElementById("pulse").value = metric.pulse;
	};

	window.editGlucose = async (id) => {
		const response = await fetch(`/get-metrics/${id}`);
		const metric = await response.json();

		document.getElementById("metricId").value = id;
		document.getElementById("glucose").value = metric.level;
	};

	// Delete metric
	window.deleteMetric = async (id) => {
		await fetch(`/delete-metrics/${id}`, { method: "DELETE" });
		fetchMetrics();
	};

	fetchMetrics();
});

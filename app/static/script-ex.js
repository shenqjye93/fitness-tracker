document.addEventListener("DOMContentLoaded", () => {
	const exerciseForm = document.getElementById("exercise-form");
	const exerciseList = document.getElementById("exercise-list");
	const links = document.querySelectorAll(".navbar a");
	const currentPath = window.location.pathname;

	links.forEach((link) => {
		if (link.getAttribute("href") === currentPath) {
			link.classList.add("active");
		} else {
			link.classList.remove("active");
		}
	});

	// Fetch and display exercises
	const fetchExercises = async (limit = 20) => {
		const response = await fetch(`/exercises?limit=${limit}`);
		const exercises = await response.json();
		renderExercises(exercises, limit);
	};

	const renderExercises = (exercises, limit = null) => {
		exerciseList.innerHTML = "";

		const exerciseArray = Object.entries(exercises)
			.filter(([_, exercise]) => exercise.category === "exercise")
			.sort(([idA], [idB]) => idB - idA)
			.slice(0, limit);

		exerciseArray.forEach(([id, exercise]) => {
			const day = getRelativeDate(id);
			const li = document.createElement("li");
			li.innerHTML = `
                    <li class="record-item">
                        <div class="record-details">
                            <strong>${exercise.name}</strong> - ${exercise.weight}kg
                            <br>
                            <small>${exercise.type} Training • ${day}, 3:30 PM</small>
                        </div>
                        <div class="record-actions">
                            <button class="btn-edit" onclick="editExercise('${id}')">Edit</button>
                            <button class="btn-delete" onclick="deleteExercise('${id}')">Delete</button>
                        </div>
                    </li>
            `;
			exerciseList.appendChild(li);
		});
	};

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

	exerciseForm.addEventListener("submit", async (e) => {
		e.preventDefault();
		const id = document.getElementById("userId").value || Date.now().toString();
		const name = document.getElementById("name").value;
		const weight = document.getElementById("weight").value;
		const type = document.getElementById("type").value;

		const method = document.getElementById("userId").value ? "PUT" : "POST";
		await fetch(`/create-exercises/${id}`, {
			method,
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				id: parseInt(id),
				name,
				weight: parseFloat(weight),
				type,
			}),
		});

		document.getElementById("exercise-form").reset();
		document.getElementById("userId").value = "";
		fetchExercises();
	});

	// Edit exercise
	window.editExercise = async (id) => {
		const response = await fetch(`/get-exercises/${id}`);
		const exercise = await response.json();

		document.getElementById("userId").value = id;
		document.getElementById("name").value = exercise.name;
		document.getElementById("weight").value = exercise.weight;
		document.getElementById("type").value = exercise.type;
	};

	// Delete exercise
	window.deleteExercise = async (id) => {
		console.log(`delete id: ${id}`);
		await fetch(`/delete-exercises/${id}`, { method: "DELETE" });
		fetchExercises();
	};

	fetchExercises();
});

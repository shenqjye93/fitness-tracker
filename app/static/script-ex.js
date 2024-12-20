document.addEventListener("DOMContentLoaded", () => {
    const exerciseForm = document.getElementById("exercise-form");
    const exerciseList = document.getElementById("exercise-list");
    const links = document.querySelectorAll('.navbar a');
    const currentPath = window.location.pathname;

    links.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
        link.classList.add('active');
        } else {
        link.classList.remove('active');
        }
    });

  // Fetch and display exercises
  const fetchExercises = async () => {
      const response = await fetch("/exercises");
      const exercises = await response.json();
      renderExercises(exercises);
  };

  // Render exercise list
  const renderExercises = (exercises) => {
      exerciseList.innerHTML = "";
      for (const id in exercises) {
          const exercise = exercises[id];

          if (exercise.category === "exercise") {
            const li = document.createElement("li");
              li.innerHTML = `
                      <li class="record-item">
                          <div class="record-details">
                              <strong>${exercise.name}</strong> - ${exercise.weight}kg
                              <br>
                              <small>${exercise.type} Training • Today, 3:30 PM</small>
                          </div>
                          <div class="record-actions">
                              <button class="btn-edit" onclick="editExercise('${id}')">Edit</button>
                              <button class="btn-delete" onclick="deleteExercise('${id}')">Delete</button>
                          </div>
                      </li>
              `;
              exerciseList.appendChild(li);
          }
      }
  };

  // Add or update exercise
 // document.querySelectorAll('.exercise-submit').forEach((button) => {
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
                body: JSON.stringify({ id: parseInt(id), name, weight: parseFloat(weight), type }),
            });

            document.getElementById("exercise-form").reset();
            document.getElementById("userId").value = "";
            fetchExercises();
            
        });
  //  });

  // Edit exercise
  window.editExercise = async (id) => {
      const response = await fetch(`/get-exercises/${id}`);
      const exercise = await response.json();

      document.getElementById("userId").value = id;
      //document.getElementById("category").value = exercise.category;
      document.getElementById("name").value = exercise.name;
      document.getElementById("weight").value = exercise.weight;
      document.getElementById("type").value = exercise.type;
  };

  // Delete exercise
  window.deleteExercise = async (id) => {
      await fetch(`/delete-exercises/${id}`, { method: "DELETE" });
      fetchExercises();
  };

  fetchExercises();
});




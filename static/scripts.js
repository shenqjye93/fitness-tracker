document.addEventListener("DOMContentLoaded", () => {
  const exerciseForm = document.getElementById("exerciseForm");
  const exerciseList = document.getElementById("exerciseList");

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
          const li = document.createElement("li");
          li.innerHTML = `
              <span class="exercise-details">
                    Exercise: ${exercise.name} <br>
                    Type: ${exercise.type} <br> 
                    Weight: ${exercise.weight} kg
                </span>
              <div>
                  <button class="edit" onclick="editExercise('${id}')">Edit</button>
                  <button class="delete" onclick="deleteExercise('${id}')">Delete</button>
              </div>
          `;
          exerciseList.appendChild(li);
      }
  };

  // Add or update exercise
  exerciseForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const id = document.getElementById("exerciseId").value || Date.now().toString();
      const name = document.getElementById("name").value;
      const weight = document.getElementById("weight").value;
      const type = document.getElementById("type").value;

      
      const method = document.getElementById("exerciseId").value ? "PUT" : "POST";
      await fetch(`/create-exercises/${id}`, {
          method,
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id: parseInt(id), name, weight: parseFloat(weight), type }),
      });

      document.getElementById("exerciseForm").reset();
      document.getElementById("exerciseId").value = "";
      fetchExercises();

      
  });

  // Edit exercise
  window.editExercise = async (id) => {
      const response = await fetch(`/get-exercises/${id}`);
      const exercise = await response.json();

      document.getElementById("exerciseId").value = id;
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

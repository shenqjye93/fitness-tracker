document.addEventListener("DOMContentLoaded", () => {
    const bpForm = document.getElementById("bp-form");
    const glucoseForm = document.getElementById("glucose-form");
    const metricList = document.getElementById("metric-list");

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
    const fetchMetrics = async () => {
        const response = await fetch("/metrics");
        const metrics = await response.json();
        renderMetrics(metrics);
    };
  
    // Render metric list
    const renderMetrics = (metrics) => {
        metricList.innerHTML = "";
        for (const id in metrics) {
            const metric = metrics[id];
  
            if (metric.type === "bp") {
              const li = document.createElement("li");
                li.innerHTML = `
                <div class="record-item">
                    <div class="record-details">
                          <strong>Blood Pressure:</strong> ${metric.level['systolic']}/${metric.level['diasystolic']} mmHg
                          <br>
                          <strong>Pulse:</strong> ${metric.level['pulse']} bpm 
                          <br>
                          <small>Today, 2:30 PM</small>
                    </div>
                    <div class="record-actions">
                        <button class="btn-edit" onclick="editBp('${id}')">Edit</button>
                        <button class="btn-delete" onclick="deleteMetric('${id}')">Delete</button>
                    </div>
                </div>
                `;
                metricList.appendChild(li);
            }

            if (metric.type === "glucose") {
                const li = document.createElement("li");
                  li.innerHTML = `
                <div class="record-item">
                    <div class="record-details">
                          <strong> Glucose:</strong> ${metric.level} mmol/L
                          <br> 
                          <small>Today, 2:30 PM</small>
                    </div>
                    <div class="record-actions">
                        <button class="btn-edit" onclick="editGlucose('${id}')">Edit</button>
                        <button class="btn-delete" onclick="deleteMetric('${id}')">Delete</button>
                    </div>
                  `;
                  metricList.appendChild(li);
    
              }
        }
    };
  
    // Add or update metric
        bpForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const id = document.getElementById("userId").value || Date.now().toString();
            const type = "bp";
            const level = {
                systolic: document.getElementById("systolic").value,
                diasystolic: document.getElementById("diasystolic").value,
                pulse: document.getElementById("pulse").value
            };
            console.log(id);
            console.log(type);
            console.log(level);


            const method = document.getElementById("userId").value ? "PUT" : "POST";
            await fetch(`/create-bp/${id}`, {
                method,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ id: parseInt(id), type, level }),
            });
    
            document.getElementById("bp-form").reset();
            document.getElementById("userId").value = "";
            fetchMetrics();
    
        });

        glucoseForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const id = document.getElementById("userId").value || Date.now().toString();
            const type = "glucose";
            const level = document.getElementById("glucose").value;
            

            const method = document.getElementById("userId").value ? "PUT" : "POST";
            await fetch(`/create-glucose/${id}`, {
                method,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ id: parseInt(id), type, level }),
            });
    
            document.getElementById("glucose-form").reset();
            document.getElementById("userId").value = "";
            fetchMetrics();
    
        });
  
    // Edit metric
    window.editBp = async (id) => {
        const response = await fetch(`/get-metrics/${id}`);
        const metric = await response.json();
  
        document.getElementById("userId").value = id;
        document.getElementById("systolic").value = metric.level['systolic']
        document.getElementById("diasystolic").value = metric.level['diasystolic']
        document.getElementById("pulse").value = metric.level['pulse']
    };

    window.editGlucose = async (id) => {
        const response = await fetch(`/get-metrics/${id}`);
        const metric = await response.json();
  
        document.getElementById("userId").value = id;
        document.getElementById("glucose").value = metric.level;
    };
  
    // Delete metric
    window.deleteMetric = async (id) => {
        await fetch(`/delete-metrics/${id}`, { method: "DELETE" });
        fetchMetrics();
    };
  
    fetchMetrics();
  });
  

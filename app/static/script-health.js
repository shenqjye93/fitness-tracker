document.addEventListener("DOMContentLoaded", () => {
    const bpForm = document.getElementById("bpForm");
    const glucoseForm = document.getElementById("glucoseForm");
    const metricList = document.getElementById("metricList");
  
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
                    <span class="metric-details">
                          Type: ${metric.type} <br>
                          Level: ${metric.level['systolic']}/${metric.level['diasystolic']} mmHg <br> 
                          Pulse: ${metric.level['pulse']} bpm
                      </span>
                    <div>
                        <button class="edit" onclick="editBp('${id}')">Edit</button>
                        <button class="delete" onclick="deleteMetric('${id}')">Delete</button>
                    </div>
                `;
                metricList.appendChild(li);
            }

            if (metric.type === "glucose") {
                const li = document.createElement("li");
                  li.innerHTML = `
                      <span class="metric-details">
                            Type: ${metric.type} <br>
                            Level: ${metric.level} mmol/L
                        </span>
                      <div>
                          <button class="edit" onclick="editGlucose('${id}')">Edit</button>
                          <button class="delete" onclick="deleteMetric('${id}')">Delete</button>
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
            console.log(level);


            const method = document.getElementById("userId").value ? "PUT" : "POST";
            await fetch(`/create-bp/${id}`, {
                method,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ id: parseInt(id), type, level }),
            });
    
            document.getElementById("bpForm").reset();
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
    
            document.getElementById("glucoseForm").reset();
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
  

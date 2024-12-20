document.addEventListener('DOMContentLoaded', () => {
    let allExercises = {};
    let exerciseChart;

    const links = document.querySelectorAll('.navbar a');
    const currentPath = window.location.pathname;

    links.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
        link.classList.add('active');
        } else {
        link.classList.remove('active');
        }
    });

    // Fetch and process data
    async function fetchData() {
        try {
            const [exercisesResponse, metricsResponse] = await Promise.all([
                fetch('/exercises'),
                fetch('/metrics')
            ]);

            const exercises = await exercisesResponse.json();
            const metrics = await metricsResponse.json();
            
            allExercises = exercises;
            createExerciseChart(exercises);
            createBPChart(metrics);
            createGlucoseChart(metrics);
            updateStreak();
            createDynamicExerciseButtons(exercises);
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    }

    function createExerciseChart(exercises, filterName = null) {
        const ctx = document.getElementById('exerciseChart').getContext('2d');
        const exerciseData = processExerciseData(exercises, filterName);

        if(exerciseChart) {
            exerciseChart.destroy();
        }


        exerciseChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: exerciseData.labels,
                datasets: [{
                    label: 'Exercise Weights',
                    data: exerciseData.weights,
                    fill: true,  
                    backgroundColor: 'rgba(156, 132, 251, 0.2)',
                    borderColor: 'rgba(156, 132, 251, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: false
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Weight (kg)',
                            color: '#929aab'
                        },
                        grid: {
                            color: '#929aab'
                        },
                        ticks: {
                            color: '#929aab'
                        },
                        border: {
                            color: 'transparent'  
                        }
                    },
                    x: {
                        title: {
                            color: '#929aab'
                        },
                        border: {
                            color: 'transparent'  
                        },
                        grid: {
                            color: 'transparent'
                        },
                        ticks: {
                            color: '#929aab'
                        },
                    }
                }
            }
        });
    }

    function processExerciseData(exercises, filterName = null) {
        const labels = [];
        const weights = [];

        for (const id in exercises) {
            const exercise = exercises[id];
            if (exercise.category === 'exercise' &&
                (filterName === null || exercise.name === filterName)) {
                labels.push(new Date(parseInt(id)).toLocaleDateString());
                weights.push(exercise.weight);
            }
        }

        return { labels, weights };
    }

    function createBPChart(metrics) {
        const ctx = document.getElementById('bpChart').getContext('2d');
        const bpData = processBPData(metrics);

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: bpData.labels,
                datasets: [
                    {
                        label: 'Systolic',
                        data: bpData.systolic,
                        borderColor: 'rgba(32, 171, 217, 1)',
                        backgroundColor: 'rgba(32, 171, 217, 1)'
                    },
                    {
                        label: 'Diasystolic',
                        data: bpData.diasystolic,
                        borderColor: 'rgba(59, 109, 194, 0.8)',
                        backgroundColor: 'rgba(59, 109, 194, 0.8)'
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        title: {
                            display: true,
                            text: 'Blood Pressure (mmHg)',
                            color: '#929aab'
                        },
                        grid: {
                            color: '#929aab'
                        },
                        ticks: {
                            color: '#929aab'
                        },
                        border: {
                            color: 'transparent'  
                        }
                    },
                    x: {
                        grid: {
                            color: 'transparent'
                        },
                        ticks: {
                            color: '#929aab'
                        },
                        border: {
                            color: 'transparent'  
                        }
                    }
                }
            }
        });
    }

    function processBPData(metrics) {
        const labels = [];
        const systolic = [];
        const diasystolic = [];

        for (const id in metrics) {
            const metric = metrics[id];
            if (metric.type === 'bp') {
                labels.push(new Date(parseInt(id)).toLocaleDateString());
                systolic.push(metric.level.systolic);
                diasystolic.push(metric.level.diasystolic);
            }
        }

        return { labels, systolic, diasystolic };
    }

    function createGlucoseChart(metrics) {
        const ctx = document.getElementById('glucoseChart').getContext('2d');
        const glucoseData = processGlucoseData(metrics);

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: glucoseData.labels,
                datasets: [{
                    label: 'Glucose Levels',
                    data: glucoseData.levels,
                    borderColor: 'rgb(116, 82, 255)',
                    backgroundColor: 'rgba(156, 132, 251, 0.8)'
                }]
            },
            options: {
                plugins: {
                    legend: false
                },
                responsive: true,
                scales: {
                    y: {
                        title: {
                            display: true,
                            text: 'Glucose (mmol/L)',
                            color: '#929aab'
                        },
                        grid: {
                            color: '#929aab'
                        },
                        ticks: {
                            color: '#929aab'
                        },
                        border: {
                            color: 'transparent'  
                        }
                    },
                    x: {
                        grid: {
                            color: 'transparent'
                        },
                        ticks: {
                            color: '#929aab'
                        },
                        border: {
                            color: 'transparent'  
                        }
                    }
                }
            }
        });
    }

    function processGlucoseData(metrics) {
        const labels = [];
        const levels = [];

        for (const id in metrics) {
            const metric = metrics[id];
            if (metric.type === 'glucose') {
                labels.push(new Date(parseInt(id)).toLocaleDateString());
                levels.push(metric.level);
            }
        }

        return { labels, levels };
    }

    function createDynamicExerciseButtons(exercises) {
        const exerciseButtonsContainer = document.getElementById('exercise-buttons');
        const uniqueExerciseTypes = new Set();

        for (const id in exercises) {
            const exercise = exercises[id];
            if (exercise.category === 'exercise') {
                uniqueExerciseTypes.add(exercise.name);
            }
        }

        uniqueExerciseTypes.forEach(name => {
            const button = document.createElement('button');
            button.textContent = name;
            button.addEventListener('click', () => {
                setActiveButton(button);
                filterExercises(name);
            });
               
            exerciseButtonsContainer.appendChild(button);
        });
    }

    function setActiveButton(activeButton) {
        // Remove "active" class from all buttons
        const buttons = document.querySelectorAll('.dynamic-buttons button');
        buttons.forEach(button => button.classList.remove('active'));
    
        // Add "active" class to the clicked button
        activeButton.classList.add('active');
    }

    function filterExercises(name) {
        createExerciseChart(allExercises, name);
        console.log(`Filtering exercises of type: ${name}`);
        console.log(`what are allexercises: ${allExercises}`);
    }

    function updateStreak() {
        // Get all exercises
        fetch('/exercises')
            .then(response => response.json())
            .then(exercises => {
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
                while (exerciseDates.has(date.toDateString()) || date.toDateString() === today) {
                    if (exerciseDates.has(date.toDateString())) {
                        currentStreak++;
                    }
                    date.setDate(date.getDate() - 1);
                }
    
                // Update streak counter display
                const streakCounter = document.querySelector('.streak-counter');
                streakCounter.innerHTML = `
                   
                    <div class="streak-calendar">
                        <span id="streakDays" class="streak-number">${currentStreak}</span>
                        <span class="streak-label">Day</span>
                        ${generateLastSevenDays(exerciseDates)}
                    </div>
                `;
            });
    }
    
    function generateLastSevenDays(exerciseDates) {
        const days = [];
        const date = new Date();
        
        // Generate last 7 days
        for (let i = 0; i < 7; i++) {
            const dateString = date.toDateString();
            const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
            const hasExercise = exerciseDates.has(dateString);
            
            days.unshift(`
                <div class="day-marker ${hasExercise ? 'logged' : 'missed'}">
                    <span class="day-name">${dayName}</span>
                    <span class="day-icon">${hasExercise ? '' : ''}</span>
                </div>
            `);
            
            date.setDate(date.getDate() - 1);
        }
        
        return days.join('');
    }

    // Initial data fetch
    fetchData();
});
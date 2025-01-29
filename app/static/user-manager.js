document.addEventListener("DOMContentLoaded", () => {
	const signupForm = document.getElementById("signup-form");
	const loginForm = document.getElementById("login-form");
	const logoutButton = document.getElementById("logout-button");
	console.log(signupForm);

	if (signupForm) {
		signupForm.addEventListener("submit", async (e) => {
			e.preventDefault();
			const username = document.getElementById("signup-username").value;
			const password = document.getElementById("signup-password").value;

			const response = await fetch("/signup", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ username, password }),
			});

			if (response.ok) {
				alert("Signup successful! Please login.");
				window.location.href = "/";
			} else {
				alert("Signup failed. Please try again.");
			}
		});
	}

	if (loginForm) {
		loginForm.addEventListener("submit", async (e) => {
			e.preventDefault();
			const username = document.getElementById("login-username").value;
			const password = document.getElementById("login-password").value;

			const response = await fetch("/login", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ username, password }),
			});

			if (response.ok) {
				window.location.href = "/dashboard/";
			} else {
				alerrt("Login failed. Please try again.");
			}
		});
	}

	if (logoutButton) {
		logoutButton.addEventListener("click", async () => {
			const response = await fetch("/logout", {
				method: "POST",
			});

			if (response.ok) {
				window.location.href = "/login.html";
			}
		});
	}
});

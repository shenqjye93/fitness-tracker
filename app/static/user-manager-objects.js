const userManagement = {
	user: null,

	async registerUser(username, password) {
		try {
			const response = await fetch("/signup", {
				method: "POST",
				header: { "Content-Type": "application/json" },
				body: JSON.stringify({ username, password }),
			});
			if (!response.ok) {
				throw new Error(
					(await response.json()).detail ||
						`HTTP error! status: ${response.status}`
				);
			}
			const user = await response.json();

			return user;
		} catch (error) {
			console.error("Registration failed:", error);
			throw error;
		}
	},

	async loginUser(username, password) {
		try {
			const response = await fetch("/login", {
				method: "POST",
				header: { "Content-Type": "application/json" },
				body: JSON.stringify({ username, password }),
			});

			if (!response.ok) {
				throw new Error(
					(await response.json()).detail || `Login failed: ${response.status}`
				);
			}

			await this.getCurrentUser();
			return true;
		} catch (error) {
			console.error("Login error:", error);
			throw error;
		}
	},

	async logoutUser() {
		try {
			const response = await fetch("/logout", {
				method: "POST",
			});

			if (!response.ok) {
				throw new Error(
					(await response.json()).detail || `Logout failed: ${response.status}`
				);
			}

			this.user = null;
			document.cookie =
				"session_cookie=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
			return true;
		} catch (error) {
			console.error("Logout error:", error);
			throw error;
		}
	},

	async getCurrentUser() {
		try {
			const userId = this.getCookie("session_cookie");

			if (!userId) {
				this.user = null;
				return null;
			}

			const response = await fetch("/me");

			if (!response.ok) {
				this.user = null;
				return null;
			}

			const user = await response.json();
			this.user = user;
			return user;
		} catch (error) {
			console.error("Error fetching current user:", error);
			this.user = null;
			return null;
		}
	},

	getCookie(name) {
		const value = `; ${document.cookie}`;
		const parts = value.split(`; ${name}=`);
		if (parts.length === 2) return parts.pop().split(";").shift();
	},

	async isAuthenticated() {
		if (this.user) {
			return true;
		}

		try {
			await this.getCurrentUser();
			return !!this.user;
		} catch (error) {
			console.error("Error during authentication check:", error);
			return false;
		}
	},
};

export default userManagement;

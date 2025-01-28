function toggleSidebar() {
	const menu = document.querySelector(".menu-toggle");
	const icon = document.querySelector(".toggle-sidebar");

	menu.classList.toggle("open");
	icon.classList.toggle("open");
}
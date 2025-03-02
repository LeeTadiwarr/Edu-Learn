import * as bootstrap from "bootstrap" // Import bootstrap

document.addEventListener("DOMContentLoaded", () => {
  // Initialize Bootstrap components
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  tooltipTriggerList.forEach((tooltipTriggerEl) => {
    new bootstrap.Tooltip(tooltipTriggerEl)
  })

  const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
  popoverTriggerList.forEach((popoverTriggerEl) => {
    new bootstrap.Popover(popoverTriggerEl)
  })

  // Handle login form submission
  const loginForm = document.getElementById("loginForm")
  if (loginForm) {
    loginForm.addEventListener("submit", (e) => {
      e.preventDefault()
      const userType = document.getElementById("userType").value
      window.location.href = `${userType}-dashboard.html`
    })
  }

  // Handle registration form submission
  const registerForm = document.getElementById("registerForm")
  if (registerForm) {
    registerForm.addEventListener("submit", (e) => {
      e.preventDefault()
      const userType = document.getElementById("registerUserType").value
      window.location.href = `${userType}-dashboard.html`
    })
  }

  // Handle sidebar toggle
  const sidebarToggle = document.getElementById("sidebarToggle")
  const sidebar = document.querySelector(".sidebar")
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener("click", () => {
      sidebar.classList.toggle("collapsed")
      // Store sidebar state in localStorage
      localStorage.setItem("sidebarCollapsed", sidebar.classList.contains("collapsed"))
    })

    // Restore sidebar state from localStorage
    const sidebarCollapsed = localStorage.getItem("sidebarCollapsed") === "true"
    if (sidebarCollapsed) {
      sidebar.classList.add("collapsed")
    }
  }

  // Handle mobile sidebar
  const mobileToggle = document.getElementById("sidebarToggleMobile")
  if (mobileToggle && sidebar) {
    mobileToggle.addEventListener("click", () => {
      sidebar.classList.toggle("active")
    })
  }

  // Handle dark mode toggle
  const darkModeToggle = document.getElementById("darkModeToggle")
  if (darkModeToggle) {
    darkModeToggle.addEventListener("click", () => {
      document.body.classList.toggle("dark-mode")
      // Store dark mode preference
      localStorage.setItem("darkMode", document.body.classList.contains("dark-mode"))
    })

    // Restore dark mode preference
    const darkMode = localStorage.getItem("darkMode") === "true"
    if (darkMode) {
      document.body.classList.add("dark-mode")
    }
  }

  // Handle form submissions with success messages
  const forms = document.querySelectorAll("form")
  forms.forEach((form) => {
    if (form.id !== "loginForm" && form.id !== "registerForm") {
      form.addEventListener("submit", (e) => {
        e.preventDefault()

        // Create success alert
        const alert = document.createElement("div")
        alert.className = "alert alert-success mt-3"
        alert.textContent = "Action completed successfully!"
        form.appendChild(alert)

        // Reset form
        form.reset()

        // Remove alert after 3 seconds
        setTimeout(() => {
          alert.remove()
        }, 3000)
      })
    }
  })

  // Handle file inputs
  const fileInputs = document.querySelectorAll('input[type="file"]')
  fileInputs.forEach((input) => {
    input.addEventListener("change", (e) => {
      const fileName = e.target.files[0]?.name
      const label = input.nextElementSibling
      if (label && fileName) {
        label.textContent = fileName
      }
    })
  })

  // Initialize date inputs with today's date as min
  const dateInputs = document.querySelectorAll('input[type="date"]')
  dateInputs.forEach((input) => {
    const today = new Date().toISOString().split("T")[0]
    input.min = today
  })
})


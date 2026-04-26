// Admin dashboard — Django REST + Token auth (base set in django-auth.js).
var API_BASE =
  typeof window.EMSI_API_BASE !== "undefined"
    ? window.EMSI_API_BASE
    : "http://127.0.0.1:8000/api/auth";

function apiTokenHeaders() {
  var t = sessionStorage.getItem("emsi_django_token");
  return {
    Authorization: "Token " + t,
    Accept: "application/json",
    "Content-Type": "application/json",
  };
}

function adminDashboard() {
  return {
    activeTab: "overview",
    userEmail: "",
    userName: "",
    userData: null,
    loading: false,
    users: [],

    showCreateUserModal: false,
    showEditUserModal: false,
    showDeleteModal: false,

    newUser: {
      email: "",
      password: "",
      first_name: "",
      last_name: "",
      role: "student",
      phone: "",
      bio: "",
    },
    editingUser: {},
    deletingUser: null,

    init() {
      this.loadUserData();
      this.setupEventListeners();
      this.startAnimations();
    },

    async loadUserData() {
      if (!window.EMSIAuth || !window.EMSIAuth.getToken()) {
        window.location.href = "login.html";
        return;
      }
      var profile = await window.EMSIAuth.getProfile();
      if (!profile || profile.role !== "admin") {
        window.location.href = "login.html";
        return;
      }
      this.userData = profile;
      this.userEmail = profile.email;
      this.userName = profile.first_name || "Admin";
      await this.loadUsers();
    },

    async loadUsers() {
      try {
        var res = await fetch(API_BASE + "/admin/users/", {
          headers: apiTokenHeaders(),
        });
        var data = await res.json().catch(function () {
          return {};
        });
        if (data.success) this.users = data.users || [];
        else console.error(data.message || "Failed to load users");
      } catch (error) {
        console.error("Error loading users:", error);
      }
    },

    async createUser() {
      this.loading = true;
      this.showDatabaseUpdating("Creating user...");

      var createdEmail = this.newUser.email;

      try {
        var response = await fetch(API_BASE + "/admin/users/create/", {
          method: "POST",
          headers: apiTokenHeaders(),
          body: JSON.stringify(this.newUser),
        });

        if (response.ok) {
          this.showCreateUserModal = false;
          this.resetNewUser();
          await this.loadUsers();
          this.hideDatabaseUpdating();
          this.showSuccessAnimation(
            '✓ User "' + createdEmail + '" added successfully!'
          );
          this.showNotification("User created successfully", "success");
        } else {
          this.hideDatabaseUpdating();
          var err = await response.json().catch(function () {
            return {};
          });
          this.showNotification(err.message || "Failed to create user", "error");
        }
      } catch (error) {
        this.hideDatabaseUpdating();
        console.error("Error creating user:", error);
        this.showNotification("Error creating user", "error");
      } finally {
        this.loading = false;
      }
    },

    editUser(user) {
      this.editingUser = Object.assign({}, user);
      this.showEditUserModal = true;
    },

    async updateUser() {
      this.loading = true;
      this.showDatabaseUpdating("Updating user...");

      try {
        var payload = {
          email: this.editingUser.email,
          first_name: this.editingUser.first_name,
          last_name: this.editingUser.last_name,
          role: this.editingUser.role,
          phone: this.editingUser.phone,
          bio: this.editingUser.bio,
          is_active: this.editingUser.is_active,
        };
        var uid = this.editingUser.id;
        var response = await fetch(
          API_BASE + "/admin/users/" + uid + "/update/",
          {
            method: "PUT",
            headers: apiTokenHeaders(),
            body: JSON.stringify(payload),
          }
        );

        if (!response.ok) {
          this.hideDatabaseUpdating();
          var err = await response.json().catch(function () {
            return {};
          });
          this.showNotification(err.message || "Update failed", "error");
          return;
        }

        this.showEditUserModal = false;
        await this.loadUsers();
        this.hideDatabaseUpdating();
        this.showSuccessAnimation(
          '✓ User "' + this.editingUser.email + '" updated successfully!'
        );
        this.showNotification("User updated successfully", "success");
      } catch (error) {
        this.hideDatabaseUpdating();
        console.error("Error updating user:", error);
        this.showNotification("Error updating user", "error");
      } finally {
        this.loading = false;
      }
    },

    confirmDeleteUser(user) {
      this.deletingUser = user;
      this.showDeleteModal = true;
    },

    async deleteUser() {
      this.loading = true;
      this.showDatabaseUpdating("Deleting user...");

      try {
        var uid = this.deletingUser.id;
        var response = await fetch(
          API_BASE + "/admin/users/" + uid + "/delete/",
          {
            method: "DELETE",
            headers: apiTokenHeaders(),
          }
        );

        if (response.ok) {
          this.showDeleteModal = false;
          var deletedEmail = this.deletingUser.email;
          this.deletingUser = null;
          await this.loadUsers();
          this.hideDatabaseUpdating();
          this.showSuccessAnimation(
            '✓ User "' + deletedEmail + '" deleted successfully!'
          );
          this.showNotification("User deleted successfully", "success");
        } else {
          this.hideDatabaseUpdating();
          var err = await response.json().catch(function () {
            return {};
          });
          this.showNotification(err.message || "Failed to delete user", "error");
        }
      } catch (error) {
        this.hideDatabaseUpdating();
        console.error("Error deleting user:", error);
        this.showNotification("Error deleting user", "error");
      } finally {
        this.loading = false;
      }
    },

    resetNewUser() {
      this.newUser = {
        email: "",
        password: "",
        first_name: "",
        last_name: "",
        role: "student",
        phone: "",
        bio: "",
      };
    },

    showDatabaseUpdating(message) {
      var indicator = document.createElement("div");
      indicator.className = "database-updating";
      indicator.id = "database-updating";
      indicator.textContent = message;
      document.body.appendChild(indicator);
    },

    hideDatabaseUpdating() {
      var indicator = document.getElementById("database-updating");
      if (indicator) indicator.remove();
    },

    showNotification(message, type) {
      var notification = document.createElement("div");
      notification.className = "notification notification-" + type;
      notification.innerHTML =
        '<div class="flex items-center">' +
        '<div class="notification-icon mr-3">' +
        (type === "success" ? "✓" : type === "error" ? "✗" : "ℹ") +
        "</div>" +
        '<div class="notification-message">' +
        message +
        "</div>" +
        '<button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-lg">&times;</button>' +
        "</div>";
      document.body.appendChild(notification);
      setTimeout(function () {
        if (notification.parentElement) notification.remove();
      }, 5000);
    },

    showSuccessAnimation(message) {
      var overlay = document.createElement("div");
      overlay.className = "success-overlay";
      overlay.innerHTML =
        '<div class="success-animation">' +
        '<div class="success-checkmark"><div class="check-icon"></div></div>' +
        '<div class="success-message">' +
        message +
        "</div></div>";
      document.body.appendChild(overlay);
      setTimeout(function () {
        overlay.classList.add("fade-out");
        setTimeout(function () {
          overlay.remove();
        }, 500);
      }, 2000);
    },

    setupEventListeners() {
      document.addEventListener(
        "keydown",
        function (e) {
          if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
              case "1":
                e.preventDefault();
                this.activeTab = "overview";
                break;
              case "2":
                e.preventDefault();
                this.activeTab = "users";
                break;
              case "3":
                e.preventDefault();
                this.activeTab = "courses";
                break;
              case "4":
                e.preventDefault();
                this.activeTab = "system";
                break;
              case "5":
                e.preventDefault();
                this.activeTab = "logs";
                break;
              case "6":
                e.preventDefault();
                this.activeTab = "settings";
                break;
            }
          }
        }.bind(this)
      );
      this.setupTypingSounds();
    },

    setupTypingSounds() {
      document.addEventListener("keydown", function () {
        try {
          var audio = new AudioContext();
          var oscillator = audio.createOscillator();
          var gainNode = audio.createGain();
          oscillator.connect(gainNode);
          gainNode.connect(audio.destination);
          oscillator.frequency.value = 800;
          oscillator.type = "square";
          gainNode.gain.value = 0.02;
          oscillator.start();
          oscillator.stop(audio.currentTime + 0.03);
        } catch (e) {}
      });
    },

    startAnimations() {
      this.createCyberGrid();
      this.createParticles();
      this.addTerminalCursor();
    },

    createCyberGrid() {
      var grid = document.createElement("div");
      grid.className = "cyber-grid";
      document.body.appendChild(grid);
    },

    createParticles() {
      var particleCount = 30;
      for (var i = 0; i < particleCount; i++) {
        setTimeout(
          function () {
            var particle = document.createElement("div");
            particle.style.cssText =
              "position:fixed;width:2px;height:2px;background:#00ff00;border-radius:50%;pointer-events:none;z-index:1;left:" +
              Math.random() * 100 +
              "%;top:" +
              Math.random() * 100 +
              "%;opacity:" +
              (0.3 + Math.random() * 0.7) +
              ";animation:float-particle " +
              (15 + Math.random() * 10) +
              "s linear infinite";
            document.body.appendChild(particle);
            setTimeout(function () {
              particle.remove();
            }, 25000);
          },
          i * 100
        );
      }
    },

    addTerminalCursor() {
      var title = document.querySelector("h1");
      if (title) title.classList.add("terminal-cursor");
    },

    async logout() {
      try {
        if (window.loginSystem) await window.loginSystem.logout();
        else window.location.href = "login.html";
      } catch (error) {
        console.error("Logout error:", error);
        window.location.href = "login.html";
      }
    },

    formatDate(dateString) {
      if (!dateString) return "N/A";
      var date = new Date(dateString);
      return date.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      });
    },

    getRoleColor(role) {
      var colors = { admin: "#ff0000", teacher: "#0099ff", student: "#00ff00" };
      return colors[role] || "#00ff00";
    },

    getStatusColor(status) {
      var colors = {
        active: "#00ff00",
        inactive: "#ff9900",
        suspended: "#ff0000",
      };
      return colors[status] || "#00ff00";
    },
  };
}

var style = document.createElement("style");
style.textContent =
  "@keyframes float-particle{0%{transform:translateY(100vh) translateX(0);opacity:0}10%{opacity:.8}90%{opacity:.8}100%{transform:translateY(-100vh) translateX(100px);opacity:0}}";
document.head.appendChild(style);

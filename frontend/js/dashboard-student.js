// Student dashboard — Django Token auth; course list stub.
function studentDashboard() {
  return {
    activeTab: "overview",
    userEmail: "",
    userName: "",
    userData: null,
    loading: false,
    _courses: [],

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
      if (!profile || profile.role !== "student") {
        window.location.href = "login.html";
        return;
      }
      this.userData = profile;
      this.userEmail = profile.email;
      this.userName = profile.first_name || "Student";
      this._courses = [];
    },

    async refreshCoursesLocal() {
      this._courses = [];
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
                this.activeTab = "courses";
                break;
              case "3":
                e.preventDefault();
                this.activeTab = "grades";
                break;
              case "4":
                e.preventDefault();
                this.activeTab = "schedule";
                break;
              case "5":
                e.preventDefault();
                this.activeTab = "resources";
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
          oscillator.frequency.value = 600;
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
      var particleCount = 20;
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
              (10 + Math.random() * 10) +
              "s linear infinite";
            document.body.appendChild(particle);
            setTimeout(function () {
              particle.remove();
            }, 20000);
          },
          i * 200
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

    async fetchGrades() {
      return [];
    },

    async fetchCourses() {
      await this.refreshCoursesLocal();
      return this._courses;
    },

    async fetchSchedule() {
      return [];
    },

    formatGrade(grade) {
      var gradeColors = {
        A: "#00ff00",
        B: "#00ff00",
        C: "#ffff00",
        D: "#ff9900",
        F: "#ff0000",
      };
      var color = gradeColors[grade.charAt(0)] || "#00ff00";
      return '<span style="color: ' + color + '">' + grade + "</span>";
    },

    formatDate(dateString) {
      var date = new Date(dateString);
      return date.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      });
    },

    getAttendanceColor(percentage) {
      if (percentage >= 90) return "#00ff00";
      if (percentage >= 80) return "#ffff00";
      if (percentage >= 70) return "#ff9900";
      return "#ff0000";
    },
  };
}

var style = document.createElement("style");
style.textContent =
  "@keyframes float-particle{0%{transform:translateY(100vh) translateX(0);opacity:0}10%{opacity:.6}90%{opacity:.6}100%{transform:translateY(-100vh) translateX(100px);opacity:0}}";
document.head.appendChild(style);

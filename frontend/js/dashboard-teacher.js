// Teacher dashboard — Django Token auth; course/student lists stubbed.
function teacherDashboard() {
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
      if (!profile || profile.role !== "teacher") {
        window.location.href = "login.html";
        return;
      }
      this.userData = profile;
      this.userEmail = profile.email;
      this.userName = profile.first_name || "Teacher";
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
                this.activeTab = "students";
                break;
              case "4":
                e.preventDefault();
                this.activeTab = "assignments";
                break;
              case "5":
                e.preventDefault();
                this.activeTab = "grades";
                break;
              case "6":
                e.preventDefault();
                this.activeTab = "schedule";
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
          oscillator.frequency.value = 700;
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
      var particleCount = 25;
      for (var i = 0; i < particleCount; i++) {
        setTimeout(
          function () {
            var particle = document.createElement("div");
            particle.style.cssText =
              "position:fixed;width:2px;height:2px;background:#0099ff;border-radius:50%;pointer-events:none;z-index:1;left:" +
              Math.random() * 100 +
              "%;top:" +
              Math.random() * 100 +
              "%;opacity:" +
              (0.3 + Math.random() * 0.7) +
              ";animation:float-particle " +
              (12 + Math.random() * 8) +
              "s linear infinite";
            document.body.appendChild(particle);
            setTimeout(function () {
              particle.remove();
            }, 20000);
          },
          i * 150
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

    async fetchCourses() {
      await this.refreshCoursesLocal();
      return this._courses;
    },

    async fetchStudents() {
      return [];
    },

    async createAssignment() {
      return null;
    },

    formatDate(dateString) {
      var date = new Date(dateString);
      return date.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      });
    },

    formatTime(timeString) {
      return new Date("2000-01-01T" + timeString).toLocaleTimeString("en-US", {
        hour: "numeric",
        minute: "2-digit",
        hour12: true,
      });
    },
  };
}

var style = document.createElement("style");
style.textContent =
  "@keyframes float-particle{0%{transform:translateY(100vh) translateX(0);opacity:0}10%{opacity:.7}90%{opacity:.7}100%{transform:translateY(-100vh) translateX(100px);opacity:0}}";
document.head.appendChild(style);

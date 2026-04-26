/**
 * Django REST auth (Token): login / profile / logout.
 * Stores the API token in sessionStorage after Django login.
 *
 * API host follows the page host (localhost vs 127.0.0.1) so Django ALLOWED_HOSTS matches.
 */
(function resolveApiBase() {
  var h = window.location.hostname;
  if (!h) h = "127.0.0.1";
  var p = window.location.protocol === "https:" ? "https:" : "http:";
  window.EMSI_API_BASE = p + "//" + h + ":8000/api/auth";
})();
var LOGIN_API_BASE = window.EMSI_API_BASE;
var TOKEN_KEY = "emsi_django_token";
var USER_KEY = "emsi_django_user";

function authHeaders() {
  var t = sessionStorage.getItem(TOKEN_KEY);
  if (!t) return { Accept: "application/json" };
  return {
    Authorization: "Token " + t,
    Accept: "application/json",
    "Content-Type": "application/json",
  };
}

var EMSIAuth = {
  getToken: function () {
    return sessionStorage.getItem(TOKEN_KEY);
  },

  clear: function () {
    sessionStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem(USER_KEY);
  },

  /** Profile from API (id, email, first_name, last_name, role, …) */
  getProfile: async function () {
    var t = sessionStorage.getItem(TOKEN_KEY);
    if (!t) return null;
    var res = await fetch(LOGIN_API_BASE + "/profile/", {
      headers: authHeaders(),
    });
    if (!res.ok) return null;
    var data = await res.json();
    if (!data.success || !data.user) return null;
    var u = data.user;
    u.role = data.role || u.role;
    sessionStorage.setItem(USER_KEY, JSON.stringify(u));
    return u;
  },
};

class DjangoAuthLoginSystem {
  async login(email, password) {
    try {
      var response = await fetch(LOGIN_API_BASE + "/login/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({ email: email, password: password }),
      });
      var data = {};
      try {
        data = await response.json();
      } catch (e) {
        return {
          success: false,
          message: "Invalid response from server. Is Django running on port 8000?",
        };
      }
      if (!response.ok || !data.success) {
        var msg = data.message;
        if (!msg && data.errors) {
          var e = data.errors;
          if (e.non_field_errors && e.non_field_errors[0]) msg = e.non_field_errors[0];
          else if (e.email && e.email[0]) msg = e.email[0];
          else if (e.password && e.password[0]) msg = e.password[0];
        }
        return {
          success: false,
          message:
            msg ||
            (response.status === 400 || response.status === 401
              ? "Invalid email or password"
              : "Login failed"),
        };
      }
      sessionStorage.setItem(TOKEN_KEY, data.token);
      sessionStorage.setItem(USER_KEY, JSON.stringify(data.user));
      return {
        success: true,
        user: data.user,
        role: data.role || data.user.role || "student",
        message: data.message || "Authentication successful",
      };
    } catch (error) {
      console.error("Login error:", error);
      return {
        success: false,
        message:
          error.message ||
          "Cannot reach the API. Start Django (port 8000) and try again.",
      };
    }
  }

  async logout() {
    try {
      var t = sessionStorage.getItem(TOKEN_KEY);
      if (t) {
        await fetch(LOGIN_API_BASE + "/logout/", {
          method: "POST",
          headers: authHeaders(),
        });
      }
    } catch (e) {}
    EMSIAuth.clear();
    return { success: true, message: "Logged out successfully" };
  }

  async isAuthenticated() {
    var t = sessionStorage.getItem(TOKEN_KEY);
    if (!t) return false;
    var res = await fetch(LOGIN_API_BASE + "/profile/", {
      headers: authHeaders(),
    });
    return res.ok;
  }

  async getCurrentUser() {
    var u = await EMSIAuth.getProfile();
    if (!u) return null;
    return {
      user: u,
      role: u.role,
      token: sessionStorage.getItem(TOKEN_KEY),
    };
  }

  redirectToDashboard(role) {
    switch (role) {
      case "admin":
        window.location.href = "dashboard-admin.html";
        break;
      case "teacher":
        window.location.href = "dashboard-teacher.html";
        break;
      case "student":
        window.location.href = "dashboard-student.html";
        break;
      default:
        window.location.href = "login.html";
    }
  }

  async validateSession() {
    return this.isAuthenticated();
  }
}

window.EMSIAuth = EMSIAuth;

document.addEventListener("DOMContentLoaded", function () {
  window.databaseLoginSystem = new DjangoAuthLoginSystem();
});
if (document.readyState !== "loading") {
  window.databaseLoginSystem = new DjangoAuthLoginSystem();
}
window.ensureDatabaseLoginSystem = function () {
  if (!window.databaseLoginSystem) {
    window.databaseLoginSystem = new DjangoAuthLoginSystem();
  }
  return window.databaseLoginSystem;
};

window.loginSystem = {
  logout: async function () {
    await window.ensureDatabaseLoginSystem().logout();
    window.location.href = "login.html";
  },
};

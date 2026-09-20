(function (global) {
  const defaults = {
    meUrl: "/auth/me",
    loginUrl: "/auth/login",
    logoutUrl: "/auth/logout",
  };

  async function getSession(options) {
    const opts = Object.assign({}, defaults, options || {});
    try {
      const response = await fetch(opts.meUrl, { credentials: "same-origin" });
      if (!response.ok) return { authenticated: false, configured: false };
      return await response.json();
    } catch {
      return { authenticated: false, configured: false };
    }
  }

  function login(options) {
    const opts = Object.assign({}, defaults, options || {});
    global.location.href = opts.loginUrl;
  }

  global.OidcAuth = { getSession, login, defaults };
})(window);

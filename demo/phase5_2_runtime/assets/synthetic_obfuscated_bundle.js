/*
 * Synthetic obfuscated JS bundle for WebAgentRuntimeBench Phase 5.2-A0.
 * Local benchmark use only. This is not a real platform signature.
 */
(function () {
  function requireRuntime(name, predicate) {
    if (!predicate()) {
      throw new ReferenceError(name + " is not defined in synthetic runtime");
    }
  }

  requireRuntime("window", function () { return typeof window !== "undefined"; });
  requireRuntime("document", function () { return typeof document !== "undefined"; });
  requireRuntime("navigator", function () { return typeof navigator !== "undefined"; });
  requireRuntime("EventTarget", function () { return typeof EventTarget !== "undefined"; });
  requireRuntime("localStorage", function () { return typeof localStorage !== "undefined"; });

  var crypto = require("node:crypto");
  var marker = ["W", "A", "R", "B", "D", "e", "m", "o", "V", "1"].join("");

  function stableJson(value) {
    if (value === null || typeof value !== "object") {
      return JSON.stringify(value);
    }
    if (Array.isArray(value)) {
      return "[" + value.map(stableJson).join(",") + "]";
    }
    return "{" + Object.keys(value).sort().map(function (key) {
      return JSON.stringify(key) + ":" + stableJson(value[key]);
    }).join(",") + "}";
  }

  function sha256(text) {
    return crypto.createHash("sha256").update(text, "utf8").digest("hex");
  }

  window.__warb_demo_sign = function (path, payload) {
    var ua = navigator.userAgent;
    var salt = localStorage.getItem("warb_demo_salt");
    var payloadText = stableJson(payload);
    var payloadHash = sha256(payloadText);
    var digest = sha256(marker + "|" + path + "|" + payloadText + "|" + ua + "|" + salt);

    return {
      header_name: "x-demo-signature",
      signature: "demo_" + digest,
      dependencies: {
        path: path,
        payload_hash: payloadHash,
        user_agent: ua,
        salt_source: "localStorage.warb_demo_salt",
        salt: salt,
        algorithm: marker
      },
      synthetic_only: true
    };
  };
}());

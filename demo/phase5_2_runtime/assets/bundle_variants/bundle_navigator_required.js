// Synthetic bundle: requires navigator.userAgent
(function () {
  var _nav = navigator;
  if (!_nav) throw new ReferenceError("navigator is not defined");
  var _ua = _nav.userAgent;
  window.__warb_demo_sign = function (path, payload) {
    var crypto = require("node:crypto");
    var stableJson = JSON.stringify(payload, Object.keys(payload).sort());
    var salt = "synthetic_salt_v1";
    var preimage = "WARBDemoV1|" + path + "|" + stableJson + "|" + _ua + "|" + salt;
    var digest = crypto.createHash("sha256").update(preimage).digest("hex");
    return {
      header_name: "x-demo-signature",
      signature: "demo_" + digest,
      dependencies: { path: path, payload_hash: crypto.createHash("sha256").update(stableJson).digest("hex"), user_agent: _ua, salt_source: "localStorage", salt: salt, algorithm: "sha256" },
      synthetic_only: true
    };
  };
})();

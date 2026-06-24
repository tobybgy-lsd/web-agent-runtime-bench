// Synthetic bundle: requires localStorage
(function () {
  var _ls = localStorage;
  if (!_ls) throw new ReferenceError("localStorage is not defined");
  var salt = _ls.getItem("warb_demo_salt") || "synthetic_salt_v1";
  window.__warb_demo_sign = function (path, payload) {
    var crypto = require("node:crypto");
    var stableJson = JSON.stringify(payload, Object.keys(payload).sort());
    var ua = "WebAgentRuntimeBench/SyntheticRuntime/1.0";
    var preimage = "WARBDemoV1|" + path + "|" + stableJson + "|" + ua + "|" + salt;
    var digest = crypto.createHash("sha256").update(preimage).digest("hex");
    return {
      header_name: "x-demo-signature",
      signature: "demo_" + digest,
      dependencies: { path: path, payload_hash: crypto.createHash("sha256").update(stableJson).digest("hex"), user_agent: ua, salt_source: "localStorage", salt: salt, algorithm: "sha256" },
      synthetic_only: true
    };
  };
})();

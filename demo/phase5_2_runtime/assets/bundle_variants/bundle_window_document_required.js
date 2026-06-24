// Synthetic bundle: requires window and document
(function () {
  var _win = window;
  var _doc = document;
  if (!_win) throw new ReferenceError("window is not defined");
  if (!_doc) throw new ReferenceError("document is not defined");
  _win.__warb_demo_sign = function (path, payload) {
    var crypto = require("node:crypto");
    var stableJson = JSON.stringify(payload, Object.keys(payload).sort());
    var ua = "WebAgentRuntimeBench/SyntheticRuntime/1.0";
    var salt = "synthetic_salt_v1";
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

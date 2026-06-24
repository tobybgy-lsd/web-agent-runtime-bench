// Synthetic bundle: requires all runtime globals
(function () {
  var _win = window;
  var _doc = document;
  var _nav = navigator;
  var _et = EventTarget;
  var _ls = localStorage;
  if (!_win) throw new ReferenceError("window is not defined");
  if (!_doc) throw new ReferenceError("document is not defined");
  if (!_nav) throw new ReferenceError("navigator is not defined");
  var _ua = _nav.userAgent;
  if (!_et) throw new ReferenceError("EventTarget is not defined");
  var demoBus = new _et();
  if (!_ls) throw new ReferenceError("localStorage is not defined");
  var salt = _ls.getItem("warb_demo_salt") || "synthetic_salt_v1";
  _win.__warb_demo_sign = function (path, payload) {
    var crypto = require("node:crypto");
    var stableJson = JSON.stringify(payload, Object.keys(payload).sort());
    var preimage = "WARBDemoV1|" + path + "|" + stableJson + "|" + _ua + "|" + salt;
    var digest = crypto.createHash("sha256").update(preimage).digest("hex");
    demoBus.dispatchEvent ? null : null;
    return {
      header_name: "x-demo-signature",
      signature: "demo_" + digest,
      dependencies: { path: path, payload_hash: crypto.createHash("sha256").update(stableJson).digest("hex"), user_agent: _ua, salt_source: "localStorage", salt: salt, algorithm: "sha256" },
      synthetic_only: true
    };
  };
})();

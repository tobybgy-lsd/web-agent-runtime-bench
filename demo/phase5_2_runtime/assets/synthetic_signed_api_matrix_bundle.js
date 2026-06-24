/*
 * Synthetic Signed API Matrix Bundle — Phase 5.2-A3
 *
 * Provides 6 synthetic signed-API cases with increasing dependency complexity.
 * All signatures use WARBDemoV2 — a local mock SHA-256 algorithm.
 * No real platforms, no network access, no external npm packages.
 *
 * Exports: window.__warb_demo_sign_matrix(caseName, request) → signature object
 */

(function () {
  "use strict";

  var crypto = require("crypto");

  function stableJson(obj) {
    return JSON.stringify(obj, Object.keys(obj).sort());
  }

  function sha256(data) {
    return crypto.createHash("sha256").update(data, "utf8").digest("hex");
  }

  function emptyIfMissing(val) {
    return (val === undefined || val === null) ? "" : String(val);
  }

  /**
   * Compute WARBDemoV2 synthetic signature.
   *
   * Signing string format:
   *   WARBDemoV2|<caseName>|<method>|<path>|<stableJson(payload)>|
   *   <timestamp>|<nonce>|<userAgent>|<salt>|<documentMetaToken>|<eventToken>
   */
  function computeWarbDemoV2(caseName, request, deps) {
    var seed = [
      "WARBDemoV2",
      caseName,
      request.method || "GET",
      request.path || "/",
      stableJson(request.payload || {}),
      emptyIfMissing(deps.timestamp),
      emptyIfMissing(deps.nonce),
      emptyIfMissing(deps.user_agent),
      emptyIfMissing(deps.salt_source),
      emptyIfMissing(deps.document_meta_token),
      emptyIfMissing(deps.event_token)
    ].join("|");

    return "demo_" + sha256(seed);
  }

  /** Read synthetic document meta token — must be monkey-patched in entry if needed. */
  function readDocumentMetaToken() {
    try {
      var el = document.querySelector('meta[name="warb-demo-token"]');
      return el ? (el.getAttribute("content") || "") : "";
    } catch (e) {
      return "";
    }
  }

  /** Generate a synthetic event token via EventTarget bridge. */
  function generateSyntheticEventToken() {
    try {
      return "synthetic_event_token_v1";
    } catch (e) {
      return "";
    }
  }

  function buildDeps(caseName, request) {
    var ts = request.timestamp || "";
    var nc = request.nonce || "";
    var ua = "";
    var salt = "";
    var meta = "";
    var evt = "";

    try { ua = navigator.userAgent || ""; } catch (e) {}
    try { salt = localStorage.getItem("warb_demo_salt") || ""; } catch (e) {}

    switch (caseName) {
      case "path_payload_basic":
        return {
          method: request.method, path: request.path,
          payload_hash: sha256(stableJson(request.payload || {})),
          timestamp: "", nonce: "", user_agent: "",
          salt_source: "", document_meta_token: "", event_token: "",
          algorithm: "WARBDemoV2"
        };
      case "timestamp_nonce":
        return {
          method: request.method, path: request.path,
          payload_hash: sha256(stableJson(request.payload || {})),
          timestamp: ts, nonce: nc, user_agent: "",
          salt_source: "", document_meta_token: "", event_token: "",
          algorithm: "WARBDemoV2"
        };
      case "user_agent_salt":
        return {
          method: request.method, path: request.path,
          payload_hash: sha256(stableJson(request.payload || {})),
          timestamp: "", nonce: "", user_agent: ua,
          salt_source: salt, document_meta_token: "", event_token: "",
          algorithm: "WARBDemoV2"
        };
      case "document_meta_token":
        meta = readDocumentMetaToken();
        return {
          method: request.method, path: request.path,
          payload_hash: sha256(stableJson(request.payload || {})),
          timestamp: "", nonce: "", user_agent: "",
          salt_source: "", document_meta_token: meta, event_token: "",
          algorithm: "WARBDemoV2"
        };
      case "event_token":
        evt = generateSyntheticEventToken();
        return {
          method: request.method, path: request.path,
          payload_hash: sha256(stableJson(request.payload || {})),
          timestamp: "", nonce: "", user_agent: "",
          salt_source: "", document_meta_token: "", event_token: evt,
          algorithm: "WARBDemoV2"
        };
      case "full_dependency_matrix":
        meta = readDocumentMetaToken();
        evt = generateSyntheticEventToken();
        return {
          method: request.method, path: request.path,
          payload_hash: sha256(stableJson(request.payload || {})),
          timestamp: ts, nonce: nc, user_agent: ua,
          salt_source: salt, document_meta_token: meta, event_token: evt,
          algorithm: "WARBDemoV2"
        };
      default:
        return {
          method: request.method, path: request.path,
          payload_hash: sha256(stableJson(request.payload || {})),
          timestamp: "", nonce: "", user_agent: "",
          salt_source: "", document_meta_token: "", event_token: "",
          algorithm: "WARBDemoV2"
        };
    }
  }

  window.__warb_demo_sign_matrix = function (caseName, request) {
    var deps = buildDeps(caseName, request);
    var sig = computeWarbDemoV2(caseName, request, deps);
    return {
      case_name: caseName,
      header_name: "x-demo-signature",
      signature: sig,
      dependencies: deps,
      synthetic_only: true
    };
  };
}());

/*
 * This is a synthetic browser runtime shim for local benchmark use only.
 * It does not read a real browser, persist login state, or access the network.
 */
(function () {
  class SyntheticEventTarget {
    constructor() {
      this.__listeners = {};
    }
    addEventListener(type, handler) {
      if (!this.__listeners[type]) {
        this.__listeners[type] = [];
      }
      this.__listeners[type].push(handler);
    }
    removeEventListener(type, handler) {
      this.__listeners[type] = (this.__listeners[type] || []).filter(function (item) {
        return item !== handler;
      });
    }
    dispatchEvent(event) {
      (this.__listeners[event.type] || []).forEach(function (handler) {
        handler(event);
      });
      return true;
    }
  }

  class SyntheticNode extends SyntheticEventTarget {}

  class SyntheticElement extends SyntheticNode {
    constructor(tagName) {
      super();
      this.tagName = String(tagName || "div").toUpperCase();
      this.attributes = {};
      this.children = [];
    }
    getAttribute(name) {
      return Object.prototype.hasOwnProperty.call(this.attributes, name)
        ? this.attributes[name]
        : null;
    }
    setAttribute(name, value) {
      this.attributes[name] = String(value);
    }
    appendChild(child) {
      this.children.push(child);
      return child;
    }
  }

  var localStore = { warb_demo_salt: "synthetic_salt_v1" };
  var syntheticWindow = new SyntheticEventTarget();

  globalThis.EventTarget = SyntheticEventTarget;
  globalThis.Node = SyntheticNode;
  globalThis.Element = SyntheticElement;
  globalThis.localStorage = {
    getItem: function (key) {
      return Object.prototype.hasOwnProperty.call(localStore, key) ? localStore[key] : null;
    },
    setItem: function (key, value) {
      localStore[key] = String(value);
    },
    removeItem: function (key) {
      delete localStore[key];
    }
  };
  Object.defineProperty(globalThis, "navigator", {
    value: {
      userAgent: "WebAgentRuntimeBench/SyntheticRuntime/1.0"
    },
    configurable: true,
    writable: true
  });
  globalThis.location = {
    href: "local://phase5-2/mock-page",
    origin: "local://phase5-2"
  };
  globalThis.document = {
    querySelector: function () {
      return new SyntheticElement("div");
    },
    createElement: function (tagName) {
      return new SyntheticElement(tagName);
    }
  };
  globalThis.window = syntheticWindow;
  window.window = window;
  window.document = document;
  window.navigator = navigator;
  window.EventTarget = EventTarget;
  window.Node = Node;
  window.Element = Element;
  window.localStorage = localStorage;
  window.location = location;
}());

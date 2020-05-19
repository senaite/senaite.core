import I18N from "./components/i18n.js";

export var i18n = new I18N();

// SENAITE message factory
var t = null;
export var _t = (msgid, keywords) => {
  if (t === null) {
    console.debug("*** Loading `senaite.core` i18n MessageFactory ***");
    i18n.loadCatalog("senaite.core")
    t = i18n.MessageFactory("senaite.core")
  }
  return t(msgid, keywords);
}

// Plone message factory
var p = null;
export var _p = (msgid, keywords) => {
  if (p === null) {
    console.debug("*** Loading `plone` i18n MessageFactory ***");
    i18n.loadCatalog("plone")
    p = i18n.MessageFactory("plone")
  }
  return p(msgid, keywords);
}

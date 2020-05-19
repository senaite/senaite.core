/* i18n integration. This is forked from jarn.jsi18n
 *
 * This is a singleton.
 * Configuration is done on the body tag data-i18ncatalogurl attribute
 *     <body data-i18ncatalogurl="/plonejsi18n">
 *
 *  Or, it'll default to "/plonejsi18n"
 */

import $ from "jquery";


var I18N = function() {
  var self = this;
  self.baseUrl = $('body').attr('data-i18ncatalogurl');
  self.currentLanguage = $('html').attr('lang') || 'en';

  // Fix for country specific languages
  if (self.currentLanguage.split('-').length > 1) {
    self.currentLanguage = self.currentLanguage.split('-')[0] + '_' + self.currentLanguage.split('-')[1].toUpperCase();
  }

  self.storage = null;
  self.catalogs = {};
  self.ttl = 24 * 3600 * 1000;

  // Internet Explorer 8 does not know Date.now() which is used in e.g. loadCatalog, so we "define" it
  if (!Date.now) {
    Date.now = function() {
      return new Date().valueOf();
    };
  }

  try {
    if ('localStorage' in window && window.localStorage !== null && 'JSON' in window && window.JSON !== null) {
      self.storage = window.localStorage;
    }
  } catch (e) {}

  self.configure = function(config) {
    for (var key in config){
      self[key] = config[key];
    }
  };

  self._setCatalog = function (domain, language, catalog) {
    if (domain in self.catalogs) {
      self.catalogs[domain][language] = catalog;
    } else {
      self.catalogs[domain] = {};
      self.catalogs[domain][language] = catalog;
    }
  };

  self._storeCatalog = function (domain, language, catalog) {
    var key = domain + '-' + language;
    if (self.storage !== null && catalog !== null) {
      self.storage.setItem(key, JSON.stringify(catalog));
      self.storage.setItem(key + '-updated', Date.now());
    }
  };

  self.getUrl = function(domain, language) {
    return self.baseUrl + '?domain=' + domain + '&language=' + language;
  };

  self.loadCatalog = function (domain, language) {
    if (language === undefined) {
      language = self.currentLanguage;
    }
    if (self.storage !== null) {
      var key = domain + '-' + language;
      if (key in self.storage) {
        if ((Date.now() - parseInt(self.storage.getItem(key + '-updated'), 10)) < self.ttl) {
          var catalog = JSON.parse(self.storage.getItem(key));
          self._setCatalog(domain, language, catalog);
          return;
        }
      }
    }
    if (!self.baseUrl) {
      return;
    }
    $.getJSON(self.getUrl(domain, language), function (catalog) {
      if (catalog === null) {
        return;
      }
      self._setCatalog(domain, language, catalog);
      self._storeCatalog(domain, language, catalog);
    });
  };

  self.MessageFactory = function (domain, language) {
    language = language || self.currentLanguage;
    return function translate (msgid, keywords) {
      var msgstr;
      if ((domain in self.catalogs) && (language in self.catalogs[domain]) && (msgid in self.catalogs[domain][language])) {
        msgstr = self.catalogs[domain][language][msgid];
      } else {
        msgstr = msgid;
      }
      if (keywords) {
        var regexp, keyword;
        for (keyword in keywords) {
          if (keywords.hasOwnProperty(keyword)) {
            regexp = new RegExp('\\$\\{' + keyword + '\\}', 'g');
            msgstr = msgstr.replace(regexp, keywords[keyword]);
          }
        }
      }
      return msgstr;
    };
  };
};

export default I18N;

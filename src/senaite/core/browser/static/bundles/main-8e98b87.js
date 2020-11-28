!function(e){var t={};function n(i){if(t[i])return t[i].exports;var o=t[i]={i:i,l:!1,exports:{}};return e[i].call(o.exports,o,o.exports,n),o.l=!0,o.exports}n.m=e,n.c=t,n.d=function(e,t,i){n.o(e,t)||Object.defineProperty(e,t,{enumerable:!0,get:i})},n.r=function(e){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},n.t=function(e,t){if(1&t&&(e=n(e)),8&t)return e;if(4&t&&"object"==typeof e&&e&&e.__esModule)return e;var i=Object.create(null);if(n.r(i),Object.defineProperty(i,"default",{enumerable:!0,value:e}),2&t&&"string"!=typeof e)for(var o in e)n.d(i,o,function(t){return e[t]}.bind(null,o));return i},n.n=function(e){var t=e&&e.__esModule?function(){return e.default}:function(){return e};return n.d(t,"a",t),t},n.o=function(e,t){return Object.prototype.hasOwnProperty.call(e,t)},n.p="/++plone++senaite.core.static/bundles",n(n.s=2)}([function(e,t){e.exports=jQuery},function(e,t,n){"use strict";(function(e){var n,i=function(e,t){return function(){return e.apply(t,arguments)}};n=function(){function t(){this.set_cookie=i(this.set_cookie,this),this.read_cookie=i(this.read_cookie,this),this.authenticator=i(this.authenticator,this),console.debug("Site::init")}return t.prototype.authenticator=function(){var t;return(t=e("input[name='_authenticator']").val())||(t=new URLSearchParams(window.location.search).get("_authenticator")),t},t.prototype.read_cookie=function(e){var t,n,i;for(console.debug("Site::read_cookie:"+e),e+="=",n=document.cookie.split(";"),i=0;i<n.length;){for(t=n[i];" "===t.charAt(0);)t=t.substring(1);if(0===t.indexOf(e))return t.substring(e.length,t.length);i++}return null},t.prototype.set_cookie=function(e,t){var n,i;console.debug("Site::set_cookie:name="+e+", value="+t),(n=new Date).setTime(n.getTime()+864e5),i="expires="+n.toUTCString(),document.cookie=e+"="+t+";"+i+";path=/"},t}(),t.a=n}).call(this,n(0))},function(e,t,n){n(4),e.exports=n(3)},function(e,t,n){},function(e,t,n){"use strict";n.r(t);var i=n(0),o=n.n(i),a=function(){var e=this;e.baseUrl=o()("body").attr("data-i18ncatalogurl"),e.currentLanguage=o()("html").attr("lang")||"en",e.currentLanguage.split("-").length>1&&(e.currentLanguage=e.currentLanguage.split("-")[0]+"_"+e.currentLanguage.split("-")[1].toUpperCase()),e.storage=null,e.catalogs={},e.ttl=864e5,Date.now||(Date.now=function(){return(new Date).valueOf()});try{"localStorage"in window&&null!==window.localStorage&&"JSON"in window&&null!==window.JSON&&(e.storage=window.localStorage)}catch(e){}e.configure=function(t){for(var n in t)e[n]=t[n]},e._setCatalog=function(t,n,i){t in e.catalogs||(e.catalogs[t]={}),e.catalogs[t][n]=i},e._storeCatalog=function(t,n,i){var o=t+"-"+n;null!==e.storage&&null!==i&&(e.storage.setItem(o,JSON.stringify(i)),e.storage.setItem(o+"-updated",Date.now()))},e.getUrl=function(t,n){return e.baseUrl+"?domain="+t+"&language="+n},e.loadCatalog=function(t,n){if(void 0===n&&(n=e.currentLanguage),null!==e.storage){var i=t+"-"+n;if(i in e.storage&&Date.now()-parseInt(e.storage.getItem(i+"-updated"),10)<e.ttl){var a=JSON.parse(e.storage.getItem(i));return void e._setCatalog(t,n,a)}}e.baseUrl&&o.a.getJSON(e.getUrl(t,n),(function(i){null!==i&&(e._setCatalog(t,n,i),e._storeCatalog(t,n,i))}))},e.MessageFactory=function(t,n){return n=n||e.currentLanguage,function(i,o){var a,r,s;if(a=t in e.catalogs&&n in e.catalogs[t]&&i in e.catalogs[t][n]?e.catalogs[t][n][i]:i,o)for(s in o)o.hasOwnProperty(s)&&(r=new RegExp("\\$\\{"+s+"\\}","g"),a=a.replace(r,o[s]));return a}}},r=null,s=function(e,t){if(null===r){var n=new a;console.debug("*** Loading `senaite.core` i18n MessageFactory ***"),n.loadCatalog("senaite.core"),r=n.MessageFactory("senaite.core")}return r(e,t)},l=null,u=function(e,t){if(null===l){var n=new a;console.debug("*** Loading `plone` i18n MessageFactory ***"),n.loadCatalog("plone"),l=n.MessageFactory("plone")}return l(e,t)},c=n(1);function g(e,t){for(var n=0;n<t.length;n++){var i=t[n];i.enumerable=i.enumerable||!1,i.configurable=!0,"value"in i&&(i.writable=!0),Object.defineProperty(e,i.key,i)}}var d=function(){function e(t){return function(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}(this,e),this.config=Object.assign({el:"sidebar",toggle_el:"sidebar-header",cookie_key:"sidebar-toggle",timeout:1e3},t),this.tid=null,this.maximize=this.maximize.bind(this),this.minimize=this.minimize.bind(this),this.on_click=this.on_click.bind(this),this.on_mouseenter=this.on_mouseenter.bind(this),this.on_mouseleave=this.on_mouseleave.bind(this),this.toggle_el=document.getElementById(this.config.toggle_el),this.toggle_el.addEventListener("click",this.on_click),this.el=document.getElementById(this.config.el),this.el.addEventListener("mouseenter",this.on_mouseenter),this.el.addEventListener("mouseleave",this.on_mouseleave),this.is_toggled()&&(this.el.classList.remove("minimized"),this.el.classList.add("toggled")),this}var t,n,i;return t=e,(n=[{key:"is_toggled",value:function(){return"true"==window.site.read_cookie(this.config.cookie_key)}},{key:"toggle",value:function(){var e=arguments.length>0&&void 0!==arguments[0]&&arguments[0];window.site.set_cookie(this.config.cookie_key,e),e?(this.el.classList.add("toggled"),this.maximize()):(this.el.classList.remove("toggled"),this.minimize())}},{key:"minimize",value:function(){this.el.classList.add("minimized")}},{key:"maximize",value:function(){this.el.classList.remove("minimized")}},{key:"on_click",value:function(e){clearTimeout(this.tid),this.toggle(!this.is_toggled())}},{key:"on_mouseenter",value:function(e){clearTimeout(this.tid),this.is_toggled()||(this.tid=setTimeout(this.maximize,this.config.timeout))}},{key:"on_mouseleave",value:function(e){clearTimeout(this.tid),this.is_toggled()||this.minimize()}}])&&g(t.prototype,n),i&&g(t,i),e}();document.addEventListener("DOMContentLoaded",(function(){console.debug("*** SENAITE CORE JS LOADED ***"),window.i18n=new a,window._t=s,window._p=u,window.portal_url=document.body.dataset.portalUrl,tinymce.init({height:300,selector:"textarea.mce_editable,div.ArchetypesRichWidget textarea,textarea[name='form.widgets.IRichTextBehavior.text'],textarea.richTextWidget",plugins:["paste","link","fullscreen","table","code"],content_css:"/++plone++senaite.core.static/bundles/main.css"}),window.site=new c.a,window.sidebar=new d({el:"sidebar"}),o()((function(){o()("[data-toggle='tooltip']").tooltip()}));var e=document.body.dataset.autoLogoff||0,t=document.body.classList.contains("userrole-authenticated");e>0&&t&&setTimeout((function(){location.href=window.portal_url+"/logout"}),60*e*1e3)}))}]);
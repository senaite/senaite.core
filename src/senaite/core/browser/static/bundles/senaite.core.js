(()=>{"use strict";var e={311:e=>{e.exports=jQuery}},t={};function n(i){var r=t[i];if(void 0!==r)return r.exports;var a=t[i]={exports:{}};return e[i](a,a.exports,n),a.exports}n.n=e=>{var t=e&&e.__esModule?()=>e.default:()=>e;return n.d(t,{a:t}),t},n.d=(e,t)=>{for(var i in t)n.o(t,i)&&!n.o(e,i)&&Object.defineProperty(e,i,{enumerable:!0,get:t[i]})},n.o=(e,t)=>Object.prototype.hasOwnProperty.call(e,t),(()=>{var e=n(311),t=n.n(e);const i=function(){var e=this;e.baseUrl=t()("body").attr("data-i18ncatalogurl"),e.currentLanguage=t()("html").attr("lang")||"en",e.currentLanguage.split("-").length>1&&(e.currentLanguage=e.currentLanguage.split("-")[0]+"_"+e.currentLanguage.split("-")[1].toUpperCase()),e.storage=null,e.catalogs={},e.ttl=864e5,Date.now||(Date.now=function(){return(new Date).valueOf()});try{"localStorage"in window&&null!==window.localStorage&&"JSON"in window&&null!==window.JSON&&(e.storage=window.localStorage)}catch(e){}e.configure=function(t){for(var n in t)e[n]=t[n]},e._setCatalog=function(t,n,i){t in e.catalogs||(e.catalogs[t]={}),e.catalogs[t][n]=i},e._storeCatalog=function(t,n,i){var r=t+"-"+n;null!==e.storage&&null!==i&&(e.storage.setItem(r,JSON.stringify(i)),e.storage.setItem(r+"-updated",Date.now()))},e.getUrl=function(t,n){return e.baseUrl+"?domain="+t+"&language="+n},e.loadCatalog=function(n,i){if(void 0===i&&(i=e.currentLanguage),null!==e.storage){var r=n+"-"+i;if(r in e.storage&&Date.now()-parseInt(e.storage.getItem(r+"-updated"),10)<e.ttl){var a=JSON.parse(e.storage.getItem(r));return void e._setCatalog(n,i,a)}}e.baseUrl&&t().getJSON(e.getUrl(n,i),(function(t){null!==t&&(e._setCatalog(n,i,t),e._storeCatalog(n,i,t))}))},e.MessageFactory=function(t,n){return n=n||e.currentLanguage,function(i,r){var a,o,l;if(a=t in e.catalogs&&n in e.catalogs[t]&&i in e.catalogs[t][n]?e.catalogs[t][n][i]:i,r)for(l in r)r.hasOwnProperty(l)&&(o=new RegExp("\\$\\{"+l+"\\}","g"),a=a.replace(o,r[l]));return a}}};var r=null,a=function(e,t){if(null===r){var n=new i;n.loadCatalog("senaite.core"),r=n.MessageFactory("senaite.core")}return r(e,t)},o=null,l=function(e,t){if(null===o){var n=new i;n.loadCatalog("plone"),o=n.MessageFactory("plone")}return o(e,t)},s=["name","error"],u=["message","level"],c=["title","message"],d=["name"],f=["name"],v=["name","message"],m=["name","message"],h=["name","value"],y=["selector","html"],_=["selector","name","value"];function g(e){return g="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},g(e)}function p(e,t){if(null==e)return{};var n,i,r=function(e,t){if(null==e)return{};var n,i,r={},a=Object.keys(e);for(i=0;i<a.length;i++)n=a[i],t.indexOf(n)>=0||(r[n]=e[n]);return r}(e,t);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);for(i=0;i<a.length;i++)n=a[i],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(r[n]=e[n])}return r}function b(e,t){var n="undefined"!=typeof Symbol&&e[Symbol.iterator]||e["@@iterator"];if(!n){if(Array.isArray(e)||(n=k(e))||t&&e&&"number"==typeof e.length){n&&(e=n);var i=0,r=function(){};return{s:r,n:function(){return i>=e.length?{done:!0}:{done:!1,value:e[i++]}},e:function(e){throw e},f:r}}throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}var a,o=!0,l=!1;return{s:function(){n=n.call(e)},n:function(){var e=n.next();return o=e.done,e},e:function(e){l=!0,a=e},f:function(){try{o||null==n.return||n.return()}finally{if(l)throw a}}}}function k(e,t){if(e){if("string"==typeof e)return w(e,t);var n=Object.prototype.toString.call(e).slice(8,-1);return"Object"===n&&e.constructor&&(n=e.constructor.name),"Map"===n||"Set"===n?Array.from(e):"Arguments"===n||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)?w(e,t):void 0}}function w(e,t){(null==t||t>e.length)&&(t=e.length);for(var n=0,i=new Array(t);n<t;n++)i[n]=e[n];return i}function S(e,t){for(var n=0;n<t.length;n++){var i=t[n];i.enumerable=i.enumerable||!1,i.configurable=!0,"value"in i&&(i.writable=!0),Object.defineProperty(e,(void 0,r=function(e,t){if("object"!==g(e)||null===e)return e;var n=e[Symbol.toPrimitive];if(void 0!==n){var i=n.call(e,"string");if("object"!==g(i))return i;throw new TypeError("@@toPrimitive must return a primitive value.")}return String(e)}(i.key),"symbol"===g(r)?r:String(r)),i)}var r}const x=function(){function e(t){!function(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}(this,e),this.config=Object.assign({form_selectors:[],field_selectors:[]},t),this.hooked_fields=[],this.on_mutated=this.on_mutated.bind(this),this.on_modified=this.on_modified.bind(this),this.on_submit=this.on_submit.bind(this),this.on_blur=this.on_blur.bind(this),this.on_click=this.on_click.bind(this),this.on_change=this.on_change.bind(this),this.on_reference_select=this.on_reference_select.bind(this),this.on_reference_deselect=this.on_reference_deselect.bind(this),this.init_forms()}var n,i;return n=e,i=[{key:"init_forms",value:function(){var e,t=b(this.config.form_selectors);try{for(t.s();!(e=t.n()).done;){var n=e.value,i=document.querySelector(n);i&&"FORM"===i.tagName&&(this.setup_form(i),this.watch_form(i))}}catch(e){t.e(e)}finally{t.f()}}},{key:"setup_form",value:function(e){this.ajax_send(e,{},"initialized")}},{key:"watch_form",value:function(e){var t,n=b(this.get_form_fields(e));try{for(n.s();!(t=n.n()).done;){var i=t.value;this.hook_field(i)}}catch(e){n.e(e)}finally{n.f()}this.observe_mutations(e),e.addEventListener("modified",this.on_modified),e.addEventListener("mutated",this.on_mutated),e.hasAttribute("ajax-submit")&&e.addEventListener("submit",this.on_submit)}},{key:"hook_field",value:function(e){-1===this.hooked_fields.indexOf(e)&&(this.is_button(e)||this.is_input_button(e)?e.addEventListener("click",this.on_click):this.is_reference(e)?(e.addEventListener("select",this.on_reference_select),e.addEventListener("deselect",this.on_reference_deselect)):this.is_text(e)||this.is_textarea(e)||this.is_select(e)?e.addEventListener("change",this.on_change):this.is_radio(e)||this.is_checkbox(e)?e.addEventListener("click",this.on_click):e.addEventListener("blur",this.on_blur),this.hooked_fields=this.hooked_fields.concat(e))}},{key:"observe_mutations",value:function(e){new MutationObserver((function(t){var n=new CustomEvent("mutated",{detail:{form:e,mutations:t}});e.dispatchEvent(n)})).observe(e,{childList:!0,subtree:!0})}},{key:"handle_mutation",value:function(e,t){var n=t.target,i=(n.closest(".field"),t.addedNodes),r=(t.removedNodes,this.config.field_selectors);if(this.is_multiple_select(n))return this.notify(e,n,"modified");if(i&&n.ELEMENT_NODE){var a,o=b(n.querySelectorAll(r));try{for(o.s();!(a=o.n()).done;){var l=a.value;this.hook_field(l)}}catch(e){o.e(e)}finally{o.f()}}}},{key:"toggle_submit",value:function(e,t){e.querySelector("input[type='submit']").disabled=!t}},{key:"toggle_field_visibility",value:function(e){var t=!(arguments.length>1&&void 0!==arguments[1])||arguments[1],n=e.closest(".field"),i="d-none";!1===t?n.classList.add(i):n.classList.remove(i)}},{key:"has_field_errors",value:function(e){return e.querySelectorAll(".is-invalid").length>0}},{key:"set_field_readonly",value:function(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:null;e.setAttribute("readonly","");var n=e.parentElement.querySelector("div.message");if(n)n.innerHTML=_t(t);else{var i=document.createElement("div");i.className="message text-secondary small",i.innerHTML=_t(t),e.parentElement.appendChild(i)}}},{key:"set_field_editable",value:function(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:null;e.removeAttribute("readonly");var n=e.parentElement.querySelector("div.message");if(n)n.innerHTML=_t(t);else{var i=document.createElement("div");i.className="message text-secondary small",i.innerHTML=_t(t),e.parentElement.appendChild(i)}}},{key:"set_field_error",value:function(e,t){e.classList.add("is-invalid");var n=e.parentElement.querySelector("div.invalid-feedback");if(n)n.innerHTML=_t(t);else{var i=document.createElement("div");i.className="invalid-feedback",i.innerHTML=_t(t),e.parentElement.appendChild(i)}}},{key:"remove_field_error",value:function(e){e.classList.remove("is-invalid");var t=e.parentElement.querySelector(".invalid-feedback");t&&t.remove()}},{key:"add_statusmessage",value:function(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:"info",n=arguments.length>2?arguments[2]:void 0;n=n||{};var i=document.createElement("div"),r=n.title||"".concat(t.charAt(0).toUpperCase()+t.slice(1));i.innerHTML='\n      <div class="alert alert-'.concat(t,' alert-dismissible fade show" role="alert">\n        <strong>').concat(r,"</strong>\n        ").concat(_t(e),'\n        <button type="button" class="close" data-dismiss="alert" aria-label="Close">\n          <span aria-hidden="true">&times;</span>\n        </button>\n      </div>\n    '),i=i.firstElementChild;var a=document.getElementById("viewlet-above-content");if(n.flush){var o,l=b(a.querySelectorAll(".alert"));try{for(l.s();!(o=l.n()).done;)o.value.remove()}catch(e){l.e(e)}finally{l.f()}}return a.appendChild(i),i}},{key:"add_notification",value:function(e,t,n){n=n||{},n=Object.assign({animation:!0,autohide:!0,delay:5e3},n);var i=document.createElement("div");i.innerHTML='\n      <div class="toast" style="width:300px" role="alert"\n           data-animation="'.concat(n.animation,'"\n           data-autohide="').concat(n.autohide,'"\n           data-delay="').concat(n.delay,'">\n        <div class="toast-header">\n          <strong class="mr-auto">').concat(e.charAt(0).toUpperCase()+e.slice(1),'</strong>\n          <button type="button" class="ml-2 mb-1 close" data-dismiss="toast" aria-label="Close">\n            <span aria-hidden="true">&times;</span>\n          </button>\n        </div>\n        <div class="toast-body">\n          ').concat(_t(t),"\n        </div>\n      </div>\n    "),i=i.firstElementChild;var r=document.querySelector(".toast-container");return r||((r=document.createElement("div")).innerHTML='\n        <div style="position: fixed; top: 0px; right: 0px; width=100%;">\n          <div class="toast-container" style="position: absolute; top: 10px; right: 10px;">\n          </div>\n        </div>\n      ',document.querySelector(".container-fluid").appendChild(r),r=r.querySelector(".toast-container")),r.appendChild(i),i}},{key:"update_form",value:function(e,n){var i,r=n.hide||[],a=n.show||[],o=n.readonly||[],l=n.editable||[],g=n.errors||[],k=n.messages||[],w=n.notifications||[],S=n.updates||[],x=n.html||[],E=n.attributes||[],L=b(g);try{for(L.s();!(i=L.n()).done;){var j,O,T=i.value;j=T.name,O=T.error,p(T,s);var C=this.get_form_field_by_name(e,j);C&&(O?this.set_field_error(C,O):this.remove_field_error(C))}}catch(e){L.e(e)}finally{L.f()}var A,q=b(k);try{for(q.s();!(A=q.n()).done;){var M,N=A.value;P=N.message,I=N.level,M=p(N,u);var I=I||"info",P=P||"";this.add_statusmessage(P,I,M)}}catch(e){q.e(e)}finally{q.f()}var U,z=b(w);try{for(z.s();!(U=z.n()).done;){var H,D,F,J=U.value;H=J.title,D=J.message,F=p(J,c);var R=this.add_notification(H,D,F);t()(R).toast("show")}}catch(e){z.e(e)}finally{z.f()}var B,X=b(r);try{for(X.s();!(B=X.n()).done;){var $,K=B.value;$=K.name,p(K,d);var Q=this.get_form_field_by_name(e,$);Q&&this.toggle_field_visibility(Q,!1)}}catch(e){X.e(e)}finally{X.f()}var G,V=b(a);try{for(V.s();!(G=V.n()).done;){var W,Y=G.value;W=Y.name,p(Y,f);var Z=this.get_form_field_by_name(e,W);Z&&this.toggle_field_visibility(Z,!0)}}catch(e){V.e(e)}finally{V.f()}var ee,te=b(o);try{for(te.s();!(ee=te.n()).done;){var ne,ie,re=ee.value;ne=re.name,ie=re.message,p(re,v);var ae=this.get_form_field_by_name(e,ne);ae&&this.set_field_readonly(ae,ie)}}catch(e){te.e(e)}finally{te.f()}var oe,le=b(l);try{for(le.s();!(oe=le.n()).done;){var se,ue,ce=oe.value;se=ce.name,ue=ce.message,p(ce,m);var de=this.get_form_field_by_name(e,se);de&&this.set_field_editable(de,ue)}}catch(e){le.e(e)}finally{le.f()}var fe,ve=b(S);try{for(ve.s();!(fe=ve.n()).done;){var me,he,ye=fe.value;me=ye.name,he=ye.value,p(ye,h);var _e=this.get_form_field_by_name(e,me);_e&&this.set_field_value(_e,he)}}catch(e){ve.e(e)}finally{ve.f()}var ge,pe=b(x);try{for(pe.s();!(ge=pe.n()).done;){var be,ke,we,Se=ge.value;be=Se.selector,ke=Se.html,we=p(Se,y);var xe=e.querySelector(be);xe&&(we.append?xe.innerHTML=xe.innerHTML+ke:xe.innerHTML=ke)}}catch(e){pe.e(e)}finally{pe.f()}var Ee,Le=b(E);try{for(Le.s();!(Ee=Le.n()).done;){var je,Oe,Te,Ce=Ee.value;je=Ce.selector,Oe=Ce.name,Te=Ce.value,p(Ce,_);var Ae=e.querySelector(je);Ae&&(null===Te?Ae.removeAttribute(Oe):Ae.addAttribute(Oe,Te))}}catch(e){Le.e(e)}finally{Le.f()}this.has_field_errors(e)?this.toggle_submit(e,!1):this.toggle_submit(e,!0)}},{key:"get_form_field_by_name",value:function(e,t){var n=e.querySelector("[name='".concat(t,"']")),i=e.querySelector("[name^='".concat(t,"']")),r=n||i||null;return null===r?null:r}},{key:"get_form_data",value:function(e){var t={};return new FormData(e).forEach((function(e,n){t[n]=e})),t}},{key:"get_form_fields",value:function(e){var t,n,i=[],r=b(this.config.field_selectors);try{for(r.s();!(t=r.n()).done;){var a,o=t.value,l=e.querySelectorAll(o);i=(a=i).concat.apply(a,function(e){if(Array.isArray(e))return w(e)}(n=l.values())||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(n)||k(n)||function(){throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}())}}catch(e){r.e(e)}finally{r.f()}return i}},{key:"get_field_name",value:function(e){return e.name.split(":")[0]}},{key:"get_field_value",value:function(e){if(this.is_checkbox(e))return e.checked;if(this.is_select(e)){var t=e.selectedOptions;return Array.prototype.map.call(t,(function(e){return e.value}))}return this.is_reference(e)?e.value.split("\n"):e.value}},{key:"set_field_value",value:function(e,t){var n=t.selected||[],i=t.options||[];if(this.is_reference(e))e.value=n.join("\n");else if(this.is_select(e)){if(0==n.length){var r=e.options[e.selected];r&&(n=[r.value])}e.options.length=0,i.sort((function(e,t){var n=e.title.toLowerCase(),i=t.title.toLowerCase();return null===e.value&&(n=""),null===t.value&&(i=""),n<i?-1:n>i?1:void 0}));var a,o=b(i);try{for(o.s();!(a=o.n()).done;){var l=a.value,s=document.createElement("option");s.value=l.value,s.innerHTML=l.title,-1!==n.indexOf(l.value)&&(s.selected=!0),e.appendChild(s)}}catch(e){o.e(e)}finally{o.f()}0==n.length&&(e.selectedIndex=0)}else this.is_checkbox(e)?e.checked=t:e.value=t}},{key:"modified",value:function(e){var t=new CustomEvent("modified",{detail:{field:e,form:e.form}});e.form.dispatchEvent(t)}},{key:"loading",value:function(){var e=new CustomEvent(arguments.length>0&&void 0!==arguments[0]&&!arguments[0]?"ajaxStop":"ajaxStart");document.dispatchEvent(e)}},{key:"notify",value:function(e,t,n){var i={name:this.get_field_name(t),value:this.get_field_value(t)};this.ajax_send(e,i,n)}},{key:"ajax_send",value:function(e,t,n){var i=document.body.dataset.viewUrl,r="".concat(i,"/ajax_form/").concat(n),a=Object.assign({form:this.get_form_data(e)},t),o={method:"POST",credentials:"include",body:JSON.stringify(a),headers:{"Content-Type":"application/json","X-CSRF-TOKEN":document.querySelector("#protect-script").dataset.token}};return this.ajax_request(e,r,o)}},{key:"ajax_submit",value:function(e,t,n){for(var i=document.body.dataset.viewUrl,r="".concat(i,"/ajax_form/").concat(n),a=new FormData(e),o=0,l=Object.entries(t);o<l.length;o++){var s=(d=l[o],f=2,function(e){if(Array.isArray(e))return e}(d)||function(e,t){var n=null==e?null:"undefined"!=typeof Symbol&&e[Symbol.iterator]||e["@@iterator"];if(null!=n){var i,r,a,o,l=[],s=!0,u=!1;try{if(a=(n=n.call(e)).next,0===t){if(Object(n)!==n)return;s=!1}else for(;!(s=(i=a.call(n)).done)&&(l.push(i.value),l.length!==t);s=!0);}catch(e){u=!0,r=e}finally{try{if(!s&&null!=n.return&&(o=n.return(),Object(o)!==o))return}finally{if(u)throw r}}return l}}(d,f)||k(d,f)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()),u=s[0],c=s[1];a.set(u,c)}var d,f,v={method:"POST",body:a};return this.ajax_request(e,r,v)}},{key:"ajax_request",value:function(e,t,n){var i=this;this.loading(!0);var r=new Request(t,n);return fetch(r).then((function(e){return e.ok?e.json():Promise.reject(e)})).then((function(t){i.update_form(e,t),i.loading(!1)})).catch((function(e){i.loading(!1)}))}},{key:"toggle_disable",value:function(e,t){e&&(e.disabled=t)}},{key:"is_textarea",value:function(e){return"TEXTAREA"==e.tagName}},{key:"is_select",value:function(e){return"SELECT"==e.tagName}},{key:"is_multiple_select",value:function(e){return this.is_select(e)&&e.hasAttribute("multiple")}},{key:"is_input",value:function(e){return"INPUT"===e.tagName}},{key:"is_text",value:function(e){return this.is_input(e)&&"text"===e.type}},{key:"is_button",value:function(e){return"BUTTON"===e.tagName}},{key:"is_input_button",value:function(e){return this.is_input(e)&&"button"===e.type}},{key:"is_checkbox",value:function(e){return this.is_input(e)&&"checkbox"===e.type}},{key:"is_radio",value:function(e){return this.is_input(e)&&"radio"===e.type}},{key:"is_reference",value:function(e){return!!this.is_textarea(e)&&e.classList.contains("queryselectwidget-value")}},{key:"on_mutated",value:function(e){var t,n=e.detail.form,i=[],r=b(e.detail.mutations);try{for(r.s();!(t=r.n()).done;){var a=t.value;i.indexOf(a.target)>-1||(i=i.concat(a.target),this.handle_mutation(n,a))}}catch(e){r.e(e)}finally{r.f()}}},{key:"on_modified",value:function(e){var t=e.detail.form,n=e.detail.field;this.notify(t,n,"modified")}},{key:"on_submit",value:function(e){var t=this;e.preventDefault();var n={},i=e.currentTarget.closest("form"),r=e.submitter;r&&(n[r.name]=r.value,this.toggle_disable(r,!0)),this.ajax_submit(i,n,"submit").then((function(e){return t.toggle_disable(r,!1)}))}},{key:"on_blur",value:function(e){var t=e.currentTarget;this.modified(t)}},{key:"on_click",value:function(e){var t=e.currentTarget;this.modified(t)}},{key:"on_change",value:function(e){var t=e.currentTarget;this.modified(t)}},{key:"on_reference_select",value:function(e){var t=e.currentTarget,n=t.value.split("\n");n=n.concat(e.detail.value),t.value=n.join("\n"),this.modified(t)}},{key:"on_reference_deselect",value:function(e){var t=e.currentTarget,n=t.value.split("\n"),i=n.indexOf(e.detail.value);i>-1&&n.splice(i,1),t.value=n.join("\n"),this.modified(t)}}],i&&S(n.prototype,i),Object.defineProperty(n,"prototype",{writable:!1}),e}();var E=n(311),L=function(e,t){return function(){return e.apply(t,arguments)}};const j=function(){function e(){this.set_cookie=L(this.set_cookie,this),this.read_cookie=L(this.read_cookie,this),this.authenticator=L(this.authenticator,this)}return e.prototype.authenticator=function(){var e;return(e=E("input[name='_authenticator']").val())||(e=new URLSearchParams(window.location.search).get("_authenticator")),e},e.prototype.read_cookie=function(e){var t,n,i;for(e+="=",n=document.cookie.split(";"),i=0;i<n.length;){for(t=n[i];" "===t.charAt(0);)t=t.substring(1);if(0===t.indexOf(e))return t.substring(e.length,t.length);i++}return null},e.prototype.set_cookie=function(e,t){var n,i;(n=new Date).setTime(n.getTime()+864e5),i="expires="+n.toUTCString(),document.cookie=e+"="+t+";"+i+";path=/"},e}();function O(e){return O="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},O(e)}function T(e,t){for(var n=0;n<t.length;n++){var i=t[n];i.enumerable=i.enumerable||!1,i.configurable=!0,"value"in i&&(i.writable=!0),Object.defineProperty(e,(void 0,r=function(e,t){if("object"!==O(e)||null===e)return e;var n=e[Symbol.toPrimitive];if(void 0!==n){var i=n.call(e,"string");if("object"!==O(i))return i;throw new TypeError("@@toPrimitive must return a primitive value.")}return String(e)}(i.key),"symbol"===O(r)?r:String(r)),i)}var r}const C=function(){function e(t){return function(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}(this,e),this.config=Object.assign({el:"sidebar",toggle_el:"sidebar-header",cookie_key:"sidebar-toggle",timeout:1e3},t),this.tid=null,this.maximize=this.maximize.bind(this),this.minimize=this.minimize.bind(this),this.on_click=this.on_click.bind(this),this.on_mouseenter=this.on_mouseenter.bind(this),this.on_mouseleave=this.on_mouseleave.bind(this),this.toggle_el=document.getElementById(this.config.toggle_el),this.toggle_el&&this.toggle_el.addEventListener("click",this.on_click),this.el=document.getElementById(this.config.el),this.el&&(this.el.addEventListener("mouseenter",this.on_mouseenter),this.el.addEventListener("mouseleave",this.on_mouseleave),this.is_toggled()&&(this.el.classList.remove("minimized"),this.el.classList.add("toggled"))),this}var t,n;return t=e,n=[{key:"is_toggled",value:function(){return"true"==window.site.read_cookie(this.config.cookie_key)}},{key:"toggle",value:function(){var e=arguments.length>0&&void 0!==arguments[0]&&arguments[0];window.site.set_cookie(this.config.cookie_key,e),e?(this.el.classList.add("toggled"),this.maximize()):(this.el.classList.remove("toggled"),this.minimize())}},{key:"minimize",value:function(){this.el.classList.add("minimized")}},{key:"maximize",value:function(){this.el.classList.remove("minimized")}},{key:"on_click",value:function(e){clearTimeout(this.tid),this.toggle(!this.is_toggled())}},{key:"on_mouseenter",value:function(e){clearTimeout(this.tid),this.is_toggled()||(this.tid=setTimeout(this.maximize,this.config.timeout))}},{key:"on_mouseleave",value:function(e){clearTimeout(this.tid),this.is_toggled()||this.minimize()}}],n&&T(t.prototype,n),Object.defineProperty(t,"prototype",{writable:!1}),e}();document.addEventListener("DOMContentLoaded",(function(){window.i18n=new i,window._t=a,window._p=l,window.portal_url=document.body.dataset.portalUrl,window.site=new j,window.sidebar=new C({el:"sidebar"}),new x({form_selectors:["form[name='edit_form']","form.senaite-ajax-form"],field_selectors:["input[type='text']","input[type='number']","input[type='checkbox']","input[type='radio']","input[type='file']","select","textarea"]}),t()((function(){t()("[data-toggle='tooltip']").tooltip(),t()("select.selectpicker").selectpicker()})),document.body.addEventListener("listing:after_transition_event",(function(e){for(var t=document.body.classList,n=0,i=["template-multi_results","template-multi_results_classic"];n<i.length;n++){var r=i[n];if(t.contains(r))return}document.body.dataset.reviewState!=e.detail.config.view_context_state&&location.reload()}))}))})()})();
//# sourceMappingURL=senaite.core.js.map
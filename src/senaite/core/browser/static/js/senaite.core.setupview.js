
/* Please use this command to compile this file into the parent directory:
    coffee --no-header -w -o ../ -c senaite.core.setupview.coffee
 */

(function() {
  var SetupViewController;

  document.addEventListener("DOMContentLoaded", function() {
    console.debug("*** DOMContentLoaded: --> Loading Controller");
    return window.setupview_controller = new SetupViewController();
  });

  SetupViewController = (function() {
    function SetupViewController() {
      var searchbox;
      this.on_search = this.on_search.bind(this);
      this.on_keypress = this.on_keypress.bind(this);
      searchbox = document.getElementById("searchbox");
      searchbox.addEventListener("input", this.on_search);
      searchbox.addEventListener("keypress", this.on_keypress);
      this.first = null;
      this.items = this.get_items();
    }

    SetupViewController.prototype.hide_tile = function(tile) {
      return tile.classList.add("d-none");
    };

    SetupViewController.prototype.show_tile = function(tile) {
      return tile.classList.remove("d-none");
    };

    SetupViewController.prototype.get_tiles = function() {
      return document.querySelectorAll("div.tilewrapper");
    };

    SetupViewController.prototype.get_items = function() {
      var items, nodes;
      nodes = document.querySelectorAll("div.tilewrapper span.title");
      items = [];
      nodes.forEach(function(el) {
        var title;
        title = el.innerText.toLowerCase();
        return items.push({
          title: title,
          el: el
        });
      });
      return items;
    };

    SetupViewController.prototype.show_all = function() {
      var tiles;
      tiles = this.get_tiles();
      return tiles.forEach((function(_this) {
        return function(tile) {
          return _this.show_tile(tile);
        };
      })(this));
    };

    SetupViewController.prototype.filter_items = function(value) {
      this.first = null;
      if (!value) {
        return this.show_all();
      }
      return this.items.forEach((function(_this) {
        return function(item) {
          var el, rx, tile, title;
          el = item.el;
          tile = el.closest("div.tilewrapper");
          title = item.title;
          rx = RegExp(value, "gi");
          if (title.match(rx)) {
            _this.show_tile(tile);
            if (_this.first === null) {
              return _this.first = tile;
            }
          } else {
            return _this.hide_tile(tile);
          }
        };
      })(this));
    };

    SetupViewController.prototype.navigate = function(tile) {
      var url;
      if (this.first === null) {
        return;
      }
      url = this.first.querySelector("a").getAttribute("href");
      if (!url) {
        return;
      }
      return location.href = url;
    };

    SetupViewController.prototype.on_search = function(event) {
      var target, value;
      target = event.currentTarget;
      value = target.value.toLowerCase();
      return this.filter_items(value);
    };

    SetupViewController.prototype.on_keypress = function(event) {
      var code;
      code = event.keyCode;
      if (code !== 13) {
        return;
      }
      return this.navigate();
    };

    return SetupViewController;

  })();

}).call(this);

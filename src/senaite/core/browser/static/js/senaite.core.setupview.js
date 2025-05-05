/**
 * SENAITE Setup View Controller
 *
 * This controller is loaded for the SENAITE Setup View, e.g. `/senaite/setup/@@lims-setup`
 */
window.SetupViewController = class SetupViewController {
  constructor() {
    this.onSearch = this.onSearch.bind(this);
    this.onKeypress = this.onKeypress.bind(this);
    this.first = null;
    this.items = this.getItems();
  }

  load() {
    console.debug("SetupViewController::load");
    this.bind_eventhandler();
  }

  bind_eventhandler() {
    console.debug("SetupViewController::bind_eventhandler");
    const $searchbox = $("#searchbox");
    $searchbox.on("input", this.onSearch);
    $searchbox.on("keypress", this.onKeypress);
  }

  hideTile(tile) {
    $(tile).addClass("d-none");
  }

  showTile(tile) {
    $(tile).removeClass("d-none");
  }

  getTiles() {
    return $("div.tilewrapper");
  }

  getItems() {
    return $("div.tilewrapper span.title").map(function () {
      return {
        title: $(this).text().toLowerCase(),
        el: this
      };
    }).get();
  }

  showAll() {
    this.getTiles().each((_, tile) => {
      this.showTile(tile);
    });
  }

  filterItems(value) {
    this.first = null;

    if (!value) {
      this.showAll();
      return;
    }

    const rx = new RegExp(value, "gi");

    this.items.forEach(item => {
      const $tile = $(item.el).closest("div.tilewrapper");
      if (item.title.match(rx)) {
        this.showTile($tile);
        if (this.first === null) {
          this.first = $tile;
        }
      } else {
        this.hideTile($tile);
      }
    });
  }

  navigate() {
    if (this.first === null) return;

    const href = this.first.find("a").attr("href");
    if (href) {
      window.location.href = href;
    }
  }

  onSearch(event) {
    const value = $(event.currentTarget).val().toLowerCase();
    this.filterItems(value);
  }

  onKeypress(event) {
    if (event.key === "Enter") {
      this.navigate();
    }
  }
}

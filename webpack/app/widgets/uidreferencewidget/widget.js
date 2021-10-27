import React from "react"
import ReactDOM from "react-dom"

import ReferenceWidgetAPI from "./api.js"
import ReferenceField from "./components/ReferenceField.js"
import ReferenceResults from "./components/ReferenceResults.js"
import References from "./components/References.js"


class UIDReferenceWidgetController extends React.Component {

  constructor(props) {
    super(props);

    // Internal state
    this.state = {
      results: [],
      searchterm: "",
      loading: false,
      count: 0,
      page: 1,
      pages: 1,
      next_url: null,
      prev_url: null,
      b_start: 1,
    }

    // root input HTML element
    let el = props.root_el;

    // data keys located at the root element
    const data_keys = [
      "id",
      "name",
      "uids",
      "api_url",
      "items",
      "catalog",
      "query",
      "columns",
      "display_template",
      "limit",
      "multi_valued",
      "disabled",
      "readonly",
    ]

    // query data keys and set state with parsed JSON value
    for (let key of data_keys) {
      let value = el.dataset[key];
      this.state[key] = this.parse_json(value);
    }

    // Prepare API
    this.api = new ReferenceWidgetAPI({
      api_url: this.state.api_url,
    });

    this.search = this.search.bind(this);
    this.goto_page = this.goto_page.bind(this);
    this.clear_results = this.clear_results.bind(this);
    this.select = this.select.bind(this);
    this.deselect = this.deselect.bind(this);
    this.on_esc = this.on_esc.bind(this);
    this.on_click = this.on_click.bind(this);

    // dev only
    window.widget = this;

    return this
  }

  componentDidMount() {
    document.addEventListener("keydown", this.on_esc, false);
    document.addEventListener("click", this.on_click, false)
  }

  componentWillUnmount() {
    document.removeEventListener("keydown", this.on_esc, false);
    document.removeEventListener("click", this.on_click, false);
  }

  /*
   * JSON parse the given value
   */
  parse_json(value) {
    try {
      return JSON.parse(value)
    } catch (error) {
      console.warn(`Could not parse "${value}" to JSON`);
    }
  }

  make_query(options) {
    options = options || {};
    return Object.assign({
      q: this.state.searchterm,
      limit: this.state.limit,
      complete: 1,
    }, options, this.state.query);
  }

  fetch_results(url_params) {
    url_params = url_params || {};
    // prepare the server request
    let self = this;
    let query = this.make_query();
    this.toggle_loading(true);
    let promise = this.api.search(this.state.catalog, query, url_params);
    promise.then(function(data) {
      console.debug(">>> GOT REFWIDGET SEARCH RESULTS: ", data);
      self.set_results_data(data)
      self.toggle_loading(false);
    });
  }

  search(value) {
    console.debug("ReferenceWidgetController::search:value:", value);
    // set the searchterm directly
    this.state.searchterm = value;
    this.fetch_results();
  }

  goto_page(page) {
    page = parseInt(page);
    let limit = parseInt(this.state.limit)
    let b_start = page * limit - limit;
    this.fetch_results({b_start: b_start});
  }

  select(uid) {
    console.debug("ReferenceWidgetController::select:uid:", uid);
    // create a copy of the selected UIDs
    let uids = [].concat(this.state.uids);
    if (uids.indexOf(uid) == -1) {
      uids.push(uid);
    }
    this.setState({uids: uids});
  }

  deselect(uid) {
    console.debug("ReferenceWidgetController::deselect:uid:", uid);
    let uids = [].concat(this.state.uids);
    let pos = uids.indexOf(uid);
    if (pos > -1) {
      uids.splice(pos, 1);
    }
    this.setState({uids: uids});
    this.clear_results();
  }

  toggle_loading(toggle) {
    if (toggle == null) {
      toggle = false;
    }
    this.setState({
      loading: toggle
    });
    return toggle;
  }

  set_results_data(data) {
    data = data || {};
    let items = data.items || [];

    let records = Object.assign(this.state.items, {})
    // update state items
    for (let item of items) {
      let uid = item.uid;
      records[uid] = item;
    }

    this.setState({
      items: records,
      results: items,
      count: data.count || 0,
      page: data.page || 1,
      pages: data.pages || 1,
      next_url: data.next || null,
      prev_url: data.previous || null,
    });
  }

  clear_results() {
    this.setState({
      results: [],
      count: 0,
      page: 1,
      pages: 1,
      next_url: null,
      prev_url: null,
    });
  }

  on_esc(event){
    // clear results when ESC key is pressed
    if(event.keyCode === 27) {
      this.clear_results();
    }
  }

  on_click(event) {
    // clear results when clicked outside of the widget
    let widget = this.props.root_el;
    let target = event.target;
    if (!widget.contains(target)) {
      this.clear_results();
    }
  }


  render() {
    return (
        <div className="uidreferencewidget">
          <References
            uids={this.state.uids}
            items={this.state.items}
            display_template={this.state.display_template}
            name={this.state.name}
            on_deselect={this.deselect}
          />
          <ReferenceField
            className="form-control"
            name="uidreference-search"
            on_search={this.search}
          />
          <ReferenceResults
            className="position-absolute shadow border rounded bg-white mt-1 p-1"
            columns={this.state.columns}
            uids={this.state.uids}
            results={this.state.results}
            count={this.state.count}
            page={this.state.page}
            pages={this.state.pages}
            next_url={this.state.next_url}
            prev_url={this.state.prev_url}
            on_select={this.select}
            on_page={this.goto_page}
          />
        </div>
    );
  }
}

export default UIDReferenceWidgetController;

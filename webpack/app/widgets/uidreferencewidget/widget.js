import React from "react"
import ReactDOM from "react-dom"

import References from "./components/References.js"
import ReferenceField from "./components/ReferenceField.js"
import ReferenceWidgetAPI from "./api.js"


class UIDReferenceWidgetController extends React.Component {

  constructor(props) {
    super(props);

    // Internal state
    this.state = {
      results: [],
      loading: false,
      count: 0,
      page: 1,
      pages: 1,
      next_url: null,
      prev_url: null
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

  search(value) {
    console.debug("ReferenceWidgetController::search:value:", value);

    let query = Object.assign({
      q: value,
      limit: this.state.limit,
      complete: 1,
    }, this.state.query);

    // prepare the server request
    let self = this;
    this.toggle_loading(true);
    let promise = this.api.search(this.state.catalog, query);
    promise.then(function(data) {
      console.debug(">>> GOT REFWIDGET SEARCH RESULTS: ", data);
      self.set_results_data(data)
      self.toggle_loading(false);
    });
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
    this.setState({
      results: data.items || [],
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
        </div>
    );
  }
}

export default UIDReferenceWidgetController;

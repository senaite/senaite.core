import React from "react"

import SearchAPI from "../../api/search.js"
import SearchField from "../components/SearchField.js"
import SearchResults from "../components/SearchResults.js"
import SelectedValues from "../components/SelectedValues.js"


class QuerySelectWidgetController extends React.Component {

  constructor(props) {
    super(props);

    // Internal state
    this.state = {
      value_key: "uid",  // result object key that has the submit value stored
      records: {},  // mapping of value -> result record
      results: [],  // `items` list of search results coming from `senaite.jsonapi`
      searchterm: "",  // the search term that was entered by the user
      loading: false,  // loading flag when searching for results
      count: 0,  // count of results (coming from `senaite.jsonapi`)
      page: 1,  // current page (coming from `senaite.jsonapi`)
      pages: 1,  // number of pages (coming from `senaite.jsonapi`)
      next_url: null,  // next page API URL (coming from `senaite.jsonapi`)
      prev_url: null,  // previous page API URL (coming from `senaite.jsonapi`)
      b_start: 1,  // batch start for pagination (see `senaite.jsonapi.batch`)
      focused: 0,  // current result that has the focus
      padding: 3,  // page padding
    }

    // Root input HTML element
    let el = props.root_el;

    // Data keys located at the root element
    // -> initial values are set from the widget class
    const data_keys = [
      "id",  // element id
      "name",  // input name that get submitted
      "values",  // selected values
      "records",  // Mapping of value -> result item
      "api_url",  // JSON API URL for search queries
      "catalog",  // catalog name
      "query",  // base catalog query
      "search_index",  // query search index
      "search_wildcard",  // make the search term a wildcard search
      "limit",  // limit to display on one page
      "value_key",  // key that contains the value that is stored
      "allow_user_value",  // allow the user to enter custom values
      "columns",  // columns to be displayed in the results popup
      "display_template",  // template to use for the selected values
      "multi_valued",  // if true, more than one value can be set
      "hide_input_after_select",  // only for single valued fields to hide the input after selection
      "disabled",  // if true, the field is rendered as not editable
      "readonly",  // if true, the field is rendered as not editable
      "padding",  // number of pages to show in navigation before and after the current
    ]

    // Query data keys and set state with parsed JSON value
    for (let key of data_keys) {
      let value = el.dataset[key];
      if (value === undefined) {
        continue;
      }
      this.state[key] = this.parse_json(value);
    }

    // Initialize communication API with the API URL
    this.api = new SearchAPI({
      api_url: this.state.api_url,
    });

    // Bind callbacks to current context
    this.search = this.search.bind(this);
    this.goto_page = this.goto_page.bind(this);
    this.clear_results = this.clear_results.bind(this);
    this.select = this.select.bind(this);
    this.select_focused = this.select_focused.bind(this);
    this.deselect = this.deselect.bind(this);
    this.set_values = this.set_values.bind(this);
    this.navigate_results = this.navigate_results.bind(this);
    this.on_keydown = this.on_keydown.bind(this);
    this.on_click = this.on_click.bind(this);

    return this
  }

  componentDidMount() {
    // Bind event listeners of the document
    document.addEventListener("keydown", this.on_keydown, false);
    document.addEventListener("click", this.on_click, false)
  }

  componentWillUnmount() {
    // Remove event listeners of the document
    document.removeEventListener("keydown", this.on_keydown, false);
    document.removeEventListener("click", this.on_click, false);
  }

  /*
   * Trigger a custom event on the textarea field that get submitted
   *
   * @param {String} event_name: The name of the event to dispatch
   * @param {Object} event_data: The data to send with the event
   */
  trigger_custom_event(event_name, event_data) {
    let event = new CustomEvent(event_name, {detail: event_data, bubbles: true});
    let field = document.querySelector(`textarea[name=${this.state.name}]`, this.props.root_el);
    if (field) {
      console.info("Dispatching Event", event);
      field.dispatchEvent(event);
    }
  }

  /*
   * JSON parse the given value
   *
   * @param {String} value: The JSON value to parse
   */
  parse_json(value) {
    try {
      return JSON.parse(value)
    } catch (error) {
      console.error(`Could not parse "${value}" to JSON`);
    }
  }

  /*
   * Checks if the field should be rendered as disabled
   *
   * @returns {Boolean} true/false if the widget is disabled
   */
  is_disabled() {
    if (this.state.disabled) {
      return true;
    }
    if (this.state.readonly) {
      return true;
    }
    if (!this.state.multi_valued && this.state.values.length > 0) {
      return true;
    }
    return false;
  }


  /*
   * Checks if the search field should be rendered after select on single valued fields
   *
   * @returns {Boolean} true/false if the search field is rendered
   */
  show_search_field() {
    if (!this.state.multi_valued && this.state.values.length > 0 && this.state.hide_input_after_select) {
      return false;
    }
    return true;
  }

  /*
   * Create a query object for the API
   *
   * This method prepares a query from the current state variables,
   * which can be used to call the `api.search` method.
   *
   * @param {Object} options: Additional options to add to the query
   * @returns {Object} The query object
   */
  make_query(options) {
    options = options || {};

    // allow to search a custom index
    // NOTE: This should be a ZCTextIndex!
    let search_index = this.state.search_index || "q";
    let search_term = this.state.searchterm;

    if (search_term && this.state.search_wildcard && !search_term.endsWith("*")) {
      search_term += "*"
    }

    let query = Object.assign({
      limit: this.state.limit,
      complete: 1,
    }, options, this.state.query);

    // inject the search index
    query[search_index] = search_term;
    return query;
  }

  /*
   * Execute a search query and set the results to the state
   *
   * @param {Object} url_params: Additional search params for the API search URL
   * @returns {Promise}
   */
  fetch_results(url_params) {
    url_params = url_params || {};
    // prepare the server request
    let self = this;
    let query = this.make_query();
    this.toggle_loading(true);
    let promise = this.api.search(this.state.catalog, query, url_params);
    promise.then(function(data) {
      console.debug("QuerySelectWidgetController::fetch_results:GOT DATA: ", data);
      self.set_results_data(data);
      self.toggle_loading(false);
    });
    return promise;
  }

  /*
   * Execute a search for the given searchterm
   *
   * @param {String} searchterm: The value entered into the search field
   * @returns {Promise}
   */
  search(searchterm) {
    if (!searchterm && this.state.results.length > 0) {
      this.state.searchterm = "";
      return;
    }
    console.debug("QuerySelectWidgetController::search:searchterm:", searchterm);
    // set the searchterm directly to avoid re-rendering
    this.state.searchterm = searchterm || "";
    return this.fetch_results();
  }

  /*
   * Fetch results of a page
   *
   * @param {Integer} page: The page to fetch
   * @returns {Promise}
   */
  goto_page(page) {
    page = parseInt(page);
    let limit = parseInt(this.state.limit)
    // calculate the beginning of the page
    // Note: this is the count of previous items that are excluded
    let b_start = page * limit - limit;
    return this.fetch_results({b_start: b_start});
  }

  /*
   * Add the value of a search result to the state
   *
   * @param {String} value: The selected value
   * @returns {Array} values: current selected values
   */
  select(value) {
    if (value === null) {
      console.warn("QuerySelectWidgetController::select: MISSING VALUE");
      return;
    }
    console.debug("QuerySelectWidgetController::select:value:", value);
    // create a copy of the selected values
    let values = [].concat(this.state.values);
    // Add the new value if it is not selected yet
    if (values.indexOf(value) == -1) {
      values.push(value);
    }
    this.setState({values: values});
    if (values.length > 0 && !this.state.multi_valued) {
      this.clear_results();
    }
    // manually trigger a select event
    this.trigger_custom_event("select", {value: value});
    return values;
  }

  /*
   * Add/remove the focused result
   *
   */
  select_focused(searchvalue) {
    console.debug("QuerySelectWidgetController::select_focused");
    let focused = this.state.focused;
    let result = this.state.results.at(focused);
    if (result) {
      let value = result[this.state.value_key];
      if (this.state.values.indexOf(value) == -1) {
        this.select(value);
      } else {
        this.deselect(value);
      }
    } else {
      if (searchvalue && this.state.allow_user_value) {
        // allow to set the current searchvalue
        this.select(searchvalue);
      }
    }
  }

  /*
   * Remove the value of a reference from the state
   *
   * @param {String} value: The selected value
   * @returns {Array} values: current selected values
   */
  deselect(value) {
    console.debug("QuerySelectWidgetController::deselect:value:", value);
    let values = [].concat(this.state.values);
    let pos = values.indexOf(value);
    if (pos > -1) {
      values.splice(pos, 1);
      // manually trigger deselect event
      this.trigger_custom_event("deselect", {value: value});
    }
    this.setState({values: values});
    return values;
  }

  /*
   * Set *all* values
   *
   * @param {Array} values: The values to be set
   */
  set_values(values) {
    this.setState({values: values});
  }

  /*
   * Navigate the results either up or down
   *
   * @param {String} direction: either up or down
   */
  navigate_results(direction) {
    let page = this.state.page;
    let pages = this.state.pages;
    let results = this.state.results;
    let focused = this.state.focused;
    let searchterm = this.state.searchterm;

    console.debug("QuerySelectWidgetController::navigate_results:focused:", focused);

    if (direction == "up") {
      if (focused > 0) {
        this.setState({focused: focused - 1});
      } else {
        this.setState({focused: 0});
        if (page > 1) {
          this.goto_page(page - 1);
        }
      }
    }

    else if (direction == "down") {
      if (this.state.results.length == 0) {
        this.search(searchterm);
      }
      if (focused < results.length - 1) {
        this.setState({focused: focused + 1});
      } else {
        this.setState({focused: 0});
        if (page < pages) {
          this.goto_page(page + 1);
        }
      }
    }

    else if (direction == "left") {
      this.setState({focused: 0});
      if (page > 0) {
        this.goto_page(page - 1);
      }
    }

    else if (direction == "right") {
      this.setState({focused: 0});
      if (page < pages) {
        this.goto_page(page + 1);
      }
    }
  }

  /*
   * Toggle loading state
   *
   * @param {Boolean} toggle: The loading state to set
   * @returns {Boolean} toggle: The current loading state
   */
  toggle_loading(toggle) {
    if (toggle == null) {
      toggle = false;
    }
    this.setState({
      loading: toggle
    });
    return toggle;
  }

  /*
   * Set results data coming from `senaite.jsonapi`
   *
   * @param {Object} data: JSON search result object returned from `senaite.jsonapi`
   */
  set_results_data(data) {
    data = data || {};
    let items = data.items || [];

    // Mapping of value -> JSON API result item
    //
    // NOTE: This is only used for UID reference field to render a friendly name
    //       for stored UIDs when the edit form is initially rendered
    let records = Object.assign(this.state.records, {})
    for (let item of items) {
      let value = item[this.state.value_key];
      records[value] = item;
    }

    this.setState({
      records: records,
      results: items,
      count: data.count || 0,
      page: data.page || 1,
      pages: data.pages || 1,
      next_url: data.next || null,
      prev_url: data.previous || null,
    });
  }

  /*
   * Clear results from the state
   */
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

  /*
   * ReactJS event handler for keydown event
   */
  on_keydown(event){
    // clear results when ESC key is pressed
    if(event.keyCode === 27) {
      this.clear_results();
    }
  }

  /*
   * ReactJS event handler for click events
   */
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
        <div id={this.state.id} className={this.props.root_class}>
          <SelectedValues
            values={this.state.values}
            records={this.state.records}
            display_template={this.state.display_template}
            name={this.state.name}
            on_deselect={this.deselect}
            set_values={this.set_values}
          />
          {this.show_search_field() &&
          <SearchField
            className="form-control"
            name="query-select-search"
            disabled={this.is_disabled()}
            on_search={this.search}
            on_clear={this.clear_results}
            on_focus={this.search}
            on_arrow_key={this.navigate_results}
            on_enter={this.select_focused}
            on_blur={this.select_focused}
          />}
          <SearchResults
            className="position-absolute shadow border rounded bg-white mt-1 p-1"
            columns={this.state.columns}
            values={this.state.values}
            value_key={this.state.value_key}
            searchterm={this.state.searchterm}
            results={this.state.results}
            focused={this.state.focused}
            count={this.state.count}
            page={this.state.page}
            pages={this.state.pages}
            padding={this.state.padding}
            next_url={this.state.next_url}
            prev_url={this.state.prev_url}
            on_select={this.select}
            on_page={this.goto_page}
            on_clear={this.clear_results}
          />
        </div>
    );
  }
}

export default QuerySelectWidgetController;

import React from "react"
import SearchAPI from "../../api/search.js"
import SearchField from "../components/SearchField.js"


class QuerySelectWidgetController extends React.Component {

  constructor(props) {
    super(props);

    // Internal state
    this.state = {
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
    //
    // Root input HTML element
    let el = props.root_el;

    // Data keys located at the root element
    // -> initial values are set from the widget class
    const data_keys = [
      "id",
      "name",
      "values",
      "api_url",
      "catalog",  // the catalog tool to query
      "query",  // the base catalog query to use
      "search_index",  // the search index to use
      "allow_user_value",  // allow the user to enter custom values
      "columns",
      "display_template",
      "limit",
      "multi_valued",
      "disabled",
      "readonly",
      "padding",
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

    window.qsw = this;

    return this;
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

    let search_index = this.state.search_index || "q";
    let search_term = this.state.searchterm;

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

    this.setState({
      results: items,
      count: data.count || 0,
      page: data.page || 1,
      pages: data.pages || 1,
      next_url: data.next || null,
      prev_url: data.previous || null,
    });
  }

  render() {
    return (
        <div className="queryselectwidget">
          <SearchField
            className="form-control"
            name="queryselect-search"
            on_search={this.search}
            on_focus={this.search}
          />
        </div>
    );
  }

}

export default QuerySelectWidgetController;

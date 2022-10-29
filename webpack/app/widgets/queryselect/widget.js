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
      "records",
      "catalog",
      "query",
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

  render() {
    return (
        <div className="queryselectwidget">
          <SearchField
            className="form-control"
            name="queryselect-search"
          />
        </div>
    );
  }

}

export default QuerySelectWidgetController;

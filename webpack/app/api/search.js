/**Search JSON API
 *
 * Use the senaite.jsonapi to search a catalog
 *
*/
class SearchAPI {

  constructor(props) {
    console.debug("SearchAPI::constructor")
    this.api_url = props.api_url;
    this.on_api_error = props.on_api_error || function() {};
    return this;
  }

  get_api_url(endpoint) {
    return `${this.api_url}/${endpoint}#${location.search}`
  }

  /*
   * Fetch Ajax API resource from the server
   *
   * @param {string} endpoint
   * @param {object} options
   * @returns {Promise}
   */
  get_json(endpoint, options) {
    var data, init, method, on_api_error, request, url;
    if (options == null) {
      options = {};
    }
    method = options.method || "POST";
    data = JSON.stringify(options.data) || "{}";
    on_api_error = this.on_api_error;
    url = this.get_api_url(endpoint);
    init = {
      method: method,
      headers: {
        "Content-Type": "application/json",
        "X-CSRF-TOKEN": this.get_csrf_token()
      },
      body: method === "POST" ? data : null,
      credentials: "include"
    };
    console.info("SearchAPI::fetch:endpoint=" + endpoint + " init=", init);
    request = new Request(url, init);
    return fetch(request).then(function(response) {
      if (!response.ok) {
        return Promise.reject(response);
      }
      return response;
    }).then(function(response) {
      return response.json();
    }).catch(function(response) {
      on_api_error(response);
      return response;
    });
  }

  search(catalog, query, params) {
    params = params || {};
    let url = `search?catalog=${catalog}`;
    for(let [key, value] of Object.entries(query)) {
      // handle arrays as repeating parameters
      if (Array.isArray(value)) {
        value.forEach( (item) => {
          url += `&${key}=${item}`;
        });
        continue;
      }
      // workaround for path queries
      if (key == "path") {
        value = value.query || null;
        if (value.depth !== null) {
          url += `&depth=${value.depth}`;
        }
      }
      if (value) {
        url += `&${key}=${value}`;
      }
    }
    for(let [key, value] of Object.entries(params)) {
      url += `&${key}=${value}`;
    }
    console.debug("SearchAPI::search:url=", url);
    return this.get_json(url, {method: "GET"});
  }

  /*
   * Get the plone.protect CSRF token
   * Note: The fields won't save w/o that token set
   */
  get_csrf_token() {
    return document.querySelector("#protect-script").dataset.token;
  }

}

export default SearchAPI;

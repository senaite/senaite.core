class AddressWidgetAPI {

  constructor(props) {
    console.debug("AddressWidgetAPI::constructor")
    this.portal_url = props.portal_url;
    this.on_api_error = props.on_api_error || function(response) {};
    return this;
  }

  get_url(endpoint) {
    return `${this.portal_url}/${endpoint}`
  }

  /*
   * Fetch JSON resource from the server
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
    url = this.get_url(endpoint);
    init = {
      method: method,
      headers: {
        "Content-Type": "application/json",
        "X-CSRF-TOKEN": this.get_csrf_token()
      },
      body: method === "POST" ? data : null,
      credentials: "include"
    };
    console.info("AddressWidgetAPI::fetch:endpoint=" + endpoint + " init=", init);
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

  fetch_subdivisions(parent) {
    let url = `geo_subdivisions`
    console.debug("AddressWidgetAPI::fetch_subdivisions:url=", url);
    let options = {
      method: "POST",
      data: {
        "parent": parent,
      }
    }
    return this.get_json(url, options)
  }

  /*
   * Get the plone.protect CSRF token
   */
  get_csrf_token() {
    return document.querySelector("#protect-script").dataset.token;
  };

}

export default AddressWidgetAPI;

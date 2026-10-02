/* Communication API for the Remarks widget */

class RemarksAPI {

  constructor(props) {
    console.debug("RemarksAPI::constructor");
    this.portal_url = props.portal_url;
    return this;
  }

  get_url(endpoint) {
    return `${this.portal_url}/${endpoint}`;
  }

  /*
   * Get the plone.protect CSRF token
   */
  get_csrf_token() {
    let el = document.querySelector("#protect-script");
    return el ? el.dataset.token : "";
  }

  /*
   * POST a JSON request to the given endpoint
   *
   * @param {string} endpoint
   * @param {object} data
   * @param {AbortSignal} signal
   * @returns {Promise}
   */
  post(endpoint, data, signal) {
    let url = this.get_url(endpoint);
    let init = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRF-TOKEN": this.get_csrf_token(),
      },
      body: JSON.stringify(data),
      credentials: "include",
      signal: signal,
    };
    let request = new Request(url, init);
    return fetch(request).then((response) => {
      if (!response.ok) {
        return Promise.reject(response);
      }
      return response.json();
    });
  }

  add_remark(uid, fieldname, value, signal) {
    let data = {uid: uid, fieldName: fieldname, value: value};
    return this.post("add_remark", data, signal);
  }

  edit_remark(uid, fieldname, remark_id, value, signal) {
    let data = {
      uid: uid,
      fieldName: fieldname,
      remark_id: remark_id,
      value: value,
    };
    return this.post("edit_remark", data, signal);
  }

  delete_remark(uid, fieldname, remark_id, signal) {
    let data = {uid: uid, fieldName: fieldname, remark_id: remark_id};
    return this.post("delete_remark", data, signal);
  }

  restore_remark(uid, fieldname, remark_id, signal) {
    let data = {uid: uid, fieldName: fieldname, remark_id: remark_id};
    return this.post("restore_remark", data, signal);
  }

  fetch_remarks(uid, fieldname, signal) {
    let data = {uid: uid, fieldName: fieldname};
    return this.post("fetch_remarks", data, signal);
  }
}

export default RemarksAPI;

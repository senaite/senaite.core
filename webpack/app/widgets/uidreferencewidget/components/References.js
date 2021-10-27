import React from "react";
import ReactDOM from "react-dom";


class References extends React.Component {

  constructor(props) {
    super(props);

    this.on_deselect = this.on_deselect.bind(this);
  }

  get_selected_uids() {
    return this.props.uids || [];
  }

  /*
   * Simple template interpolation that replaces ${...} placeholders
   * with any found value from the context object.
   *
   * https://stackoverflow.com/questions/29182244/convert-a-string-to-a-template-string
   */
  interpolate(template, context) {
    for(let [key, value] of Object.entries(context)) {
      template = template.replace(new RegExp('\\$\\{' + key + '\\}', 'g'), value)
    }
    return template;
  }

  render_display_template(uid) {
    let template = this.props.display_template;
    let context = this.props.items[uid];
    if (!context) return uid;
    return this.interpolate(template, context);
  }

  build_selected_items() {
    let items = [];
    let selected_uids = this.get_selected_uids();

    for (let uid of selected_uids) {
      items.push(
        <li uid={uid}>
          <div className="p-1 mb-1 bg-light border rounded d-inline-block">
            <span dangerouslySetInnerHTML={{__html: this.render_display_template(uid)}}></span>
            <button uid={uid}
                    className="btn btn-sm btn-link-danger"
                    onClick={this.on_deselect}>
              <i className="fas fa-times-circle"></i>
            </button>
          </div>

        </li>
      );
    }
    return items
  }

  on_deselect(event) {
    event.preventDefault();
    let target = event.currentTarget;
    let uid = target.getAttribute("uid");
    console.debug("References::on_deselect: Remove UID", uid);
    if (this.props.on_deselect) {
      this.props.on_deselect(uid);
    }
  }

  render() {
    return (
      <div className="uidreferencewidget-references">
        <ul className="list-unstyled">
          {this.build_selected_items()}
        </ul>
        {/* submitted in form */}
        <textarea
          className="d-none"
          name={this.props.name}
          value={this.props.uids.join("\n")}
        />
      </div>
    );
  }
}

export default References;

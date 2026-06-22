import React from "react";


/**
 * Collapsible list of prior versions of a remark, newest first.
 */
class VersionHistory extends React.Component {

  render() {
    let versions = this.props.versions || [];
    let i18n = this.props.i18n || {};
    if (versions.length === 0) {
      return null;
    }
    return (
      <div className="remarks-versions">
        {versions.map((version, index) => (
          <div className="remark-version" key={index}>
            <div className="remark-version-meta">
              <span className="remark-author">{version.user_id}</span>
              <span className="remark-time">{version.created}</span>
              {index === versions.length - 1 &&
                <span className="remark-original">
                  ({i18n.original || "original"})
                </span>}
            </div>
            <div
              className="remark-version-content"
              dangerouslySetInnerHTML={{__html: version.content_html}}>
            </div>
          </div>
        ))}
      </div>
    );
  }
}

export default VersionHistory;

import React from "react";
import Dropzone from "react-dropzone";
import $ from "jquery";
import "./multiupload.css";


class MultiUploadWidgetController extends React.Component {

  constructor(props) {
    super(props);

    // Root input HTML element
    let el = props.root_el;

    this.state = {
      files: [],
      uploaded_files: [],
      existing_uids: [],
    };

    // Data keys located at the root element
    const data_keys = [
      "fieldname",
      "portal_url",
      "context_url",
      "endpoint",
      "max_filesize",
      // https://react-dropzone.js.org/#section-accepting-specific-file-types
      "accepted_types",
      "existing_files",  // Metadata for existing files
    ];

    // Query data keys and set state with parsed JSON value
    for (let key of data_keys) {
      let value = el.dataset[key];
      this.state[key] = this.parse_json(value);
    }

    // Initialize existing files for display
    const existing_files = this.state.existing_files || [];
    if (existing_files.length > 0) {
      this.state.files = existing_files.map(file => ({
        id: file.uid,
        uid: file.uid,
        name: file.name,
        size: file.size || 0,
        type: file.type,
        url: file.url,
        status: "existing",
        is_existing: true,
      }));
      this.state.existing_uids = existing_files.map(file => file.uid);
    }

    // Bind callbacks
    this.onDrop = this.onDrop.bind(this);
    this.removeFile = this.removeFile.bind(this);

    return this;
  }

  /*
   * JSON parse the given value
   *
   * @param {String} value: The JSON value to parse
   */
  parse_json(value) {
    try {
      return JSON.parse(value);
    } catch (error) {
      // Return value as-is if not valid JSON
      return value;
    }
  }

  onDrop(acceptedFiles) {
    console.debug("Files dropped:", acceptedFiles);

    const newFiles = acceptedFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      file: file,
      name: file.name,
      size: file.size,
      type: file.type,
      preview: URL.createObjectURL(file),
      status: "pending",
    }));

    this.setState(
      prevState => ({
        files: [...prevState.files, ...newFiles]
      }),
      () => {
        // Upload files after state update
        newFiles.forEach(fileObj => this.uploadFile(fileObj));
      }
    );
  }

  uploadFile(fileObj) {
    const formData = new FormData();
    formData.append(this.state.fieldname, fileObj.file);

    // Update file status to uploading
    this.setState(prevState => ({
      files: prevState.files.map(f =>
        f.id === fileObj.id ? { ...f, status: "uploading", progress: 0 } : f
      )
    }));

    const endpoint = this.state.endpoint || "@@multiupload_handler";
    fetch(`${this.state.context_url}/${endpoint}`, {
      method: "POST",
      body: formData,
    })
      .then(response => {
        // Check if the response is OK
        if (!response.ok) {
          // Try to parse error message from JSON response
          return response.json().then(errorData => {
            return errorData;
          }).catch(jsonError => {
            // If JSON parsing fails, return a generic error object
            return {
              "status": "error",
              "error": `Server error: ${response.status} ${response.statusText}`
            };
          });
        }
        return response.json();
      })
      .then(data => {
        // Check if the response contains an error status
        if (data.status === "error") {
          throw new Error(data.error || "Upload failed");
        }

        console.debug("Upload success:", data);
        this.setState(prevState => ({
          files: prevState.files.map(f =>
            f.id === fileObj.id
              ? { ...f, status: "success", server_id: data.id, upload_id: data.id }
              : f
          ),
          uploaded_files: [...prevState.uploaded_files, data.id]
        }));
      })
      .catch(error => {
        console.error("Upload error:", error);
        this.setState(prevState => ({
          files: prevState.files.map(f =>
            f.id === fileObj.id
              ? { ...f, status: "error", error: error.message }
              : f
          )
        }));
      });
  }

  removeFile(fileId, event) {
    // Get the file item element and animate fade out
    const fileItem = $(event.target).closest(".multi-upload-file-item");

    // Fade out animation
    fileItem.fadeOut(300, () => {
      // After animation completes, update state
      this.setState(prevState => {
        const fileToRemove = prevState.files.find(f => f.id === fileId);
        if (!fileToRemove) return prevState;

        const newFiles = prevState.files.filter(f => f.id !== fileId);

        // Handle removal of uploaded files (new uploads)
        const newUploadedFiles = prevState.uploaded_files.filter(
          id => id !== fileToRemove.server_id
        );

        // Handle removal of existing files (already stored)
        const newExistingUids = prevState.existing_uids.filter(
          uid => uid !== fileToRemove.uid
        );

        // Revoke object URL to prevent memory leaks
        if (fileToRemove.preview) {
          URL.revokeObjectURL(fileToRemove.preview);
        }

        return {
          files: newFiles,
          uploaded_files: newUploadedFiles,
          existing_uids: newExistingUids
        };
      });
    });
  }

  formatFileSize(bytes) {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 10) / 10 + " " + sizes[i];
  }

  renderFileList() {
    if (this.state.files.length === 0) {
      return null;
    }

    return (
      <div className="multi-upload-file-list mt-3">
        {this.state.files.map((fileObj) => (
          <div key={fileObj.id} className="multi-upload-file-item border rounded p-2 mb-2">
            <div className="d-flex align-items-center justify-content-between">
              <div className="file-info d-flex align-items-center flex-grow-1">
                <span className="file-icon mr-2">📎</span>
                <div className="file-details">
                  {fileObj.is_existing && fileObj.url ? (
                    <div className="file-name font-weight-bold">
                      <a href={fileObj.url} target="_blank" rel="noopener noreferrer">
                        {fileObj.name}
                      </a>
                    </div>
                  ) : (
                    <div className="file-name font-weight-bold">{fileObj.name}</div>
                  )}
                  <div className="file-size small text-muted">
                    {this.formatFileSize(fileObj.size)}
                  </div>
                </div>
              </div>
              <div className="file-status d-flex align-items-center">
                {fileObj.status === "uploading" && (
                  <span className="badge badge-info mr-2">Uploading...</span>
                )}
                {fileObj.status === "success" && (
                  <span className="badge badge-success mr-2">✓ Uploaded</span>
                )}
                {fileObj.status === "existing" && (
                  <span className="badge badge-secondary mr-2">Saved</span>
                )}
                {fileObj.status === "error" && (
                  <span className="badge badge-danger mr-2">✗ Error</span>
                )}
                <button
                  type="button"
                  className="btn"
                  onClick={(e) => this.removeFile(fileObj.id, e)}
                  disabled={fileObj.status === "uploading"}>
                  <i className="fas fa-trash-alt text-secondary"></i>
                </button>
              </div>
            </div>
            {fileObj.status === "error" && fileObj.error && (
              <div className="alert alert-danger mt-2 mb-0 small">
                {fileObj.error}
              </div>
            )}
          </div>
        ))}
      </div>
    );
  }

  render() {
    // https://react-dropzone.js.org/#section-components
    const maxSize = this.state.max_filesize || 10485760; // 10MB default
    const accept = this.state.accepted_types || {};

    return (
      <div className="multiuploadwidget">
        <Dropzone
          onDrop={this.onDrop}
          maxSize={maxSize}
          accept={accept}>
          {({ getRootProps, getInputProps, isDragActive }) => (
            <div
              {...getRootProps()}
              className={`multi-upload-dropzone border rounded p-4 text-center ${
                isDragActive ? "drag-active" : ""
              }`}>
              <input {...getInputProps()} />
              <div className="dropzone-content">
                <span className="upload-icon" style={{ fontSize: "2rem" }}>
                  &#8682;
                </span>
                <p className="mt-2 mb-0">
                  {isDragActive
                    ? "Drop files here..."
                    : "Drag & drop files here, or click to select files"}
                </p>
                <p className="small text-muted mt-1">
                  Maximum file size: {this.formatFileSize(maxSize)}
                </p>
              </div>
            </div>
          )}
        </Dropzone>

        {this.renderFileList()}

        {/* Hidden field to store existing UIDs (maintained by React) */}
        <input
          type="hidden"
          name={this.state.fieldname}
          value={this.state.existing_uids.join("\r\n")}
        />

        {/* Hidden field to store uploaded file IDs */}
        <input
          type="hidden"
          id={`${this.state.fieldname}-data`}
          name={`${this.state.fieldname}.data`}
          value={JSON.stringify(this.state.uploaded_files)}
        />
      </div>
    );
  }
}

export default MultiUploadWidgetController;

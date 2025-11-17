(function() {
  'use strict';

  /**
   * Initialize a multi-upload widget
   */
  function initializeMultiUploadWidget(dropzoneId, triggerId, contextUrl, fieldName) {
    console.log('Attempting to initialize Dropzone with ID:', dropzoneId);

    var dropzoneElement = document.getElementById(dropzoneId);
    var triggerButton = document.getElementById(triggerId);

    if (!dropzoneElement) {
      console.error('Dropzone element not found:', dropzoneId);
      console.log('Available elements:', document.querySelectorAll('[id*="upload"]'));
      return;
    }

    if (!triggerButton) {
      console.error('Trigger button not found:', triggerId);
      return;
    }

    console.log('Dropzone element found:', dropzoneElement);
    console.log('Trigger button found:', triggerButton);

    if (typeof Dropzone === 'undefined') {
      console.error('Dropzone library not loaded');
      return;
    }

    console.log('Creating Dropzone instance...');

    try {
      var myDropzone = new Dropzone(dropzoneElement, {
        url: contextUrl + '/@@multiupload_handler',
        paramName: fieldName,
        maxFilesize: 100, // MB
        addRemoveLinks: true,
        autoProcessQueue: true, // Upload automatically when files are added
        clickable: triggerButton, // Use our button element directly
        dictDefaultMessage: 'Drop files here',
        dictRemoveFile: 'Remove',
        dictCancelUpload: 'Cancel',
        init: function() {
          var dz = this;

          // Handle file added
          this.on('addedfile', function(file) {
            console.log('File added:', file.name);
          });

          // Handle successful upload
          this.on('success', function(file, response) {
            console.log('Upload success:', file.name, response);
            file.serverId = response.id;
            updateHiddenField();
          });

          // Handle upload error
          this.on('error', function(file, errorMessage) {
            console.error('Upload error:', file.name, errorMessage);
          });

          // Handle file removed
          this.on('removedfile', function(file) {
            console.log('File removed:', file.name);
            updateHiddenField();
          });

          function updateHiddenField() {
            var fileIds = [];
            dz.files.forEach(function(f) {
              if (f.serverId) {
                fileIds.push(f.serverId);
              }
            });
            var hiddenInput = document.getElementById(dropzoneId + '-data');
            if (hiddenInput) {
              hiddenInput.value = JSON.stringify(fileIds);
            }
          }
        }
      });

      console.log('Dropzone instance created successfully:', myDropzone);

    } catch (e) {
      console.error('Error creating Dropzone instance:', e);
      console.error('Error details:', e.message, e.stack);
    }
  }

  /**
   * Initialize all multi-upload widgets on the page
   */
  function initializeAllMultiUploadWidgets() {
    var widgets = document.querySelectorAll('.multi-upload-dropzone');
    for (var i = 0; i < widgets.length; i++) {
      var dropzoneElement = widgets[i];
      var dropzoneId = dropzoneElement.id;
      var triggerId = dropzoneId + '-trigger';
      var contextUrl = dropzoneElement.getAttribute('data-context-url');
      var fieldName = dropzoneElement.getAttribute('data-field-name');

      if (dropzoneId && contextUrl && fieldName) {
        initializeMultiUploadWidget(dropzoneId, triggerId, contextUrl, fieldName);
      }
    }
  }

  // Initialize on DOMContentLoaded
  if (document.readyState === 'loading') {
    console.log('Waiting for DOMContentLoaded...');
    document.addEventListener('DOMContentLoaded', initializeAllMultiUploadWidgets);
  } else {
    // DOM already loaded
    console.log('DOM already loaded, initializing immediately');
    initializeAllMultiUploadWidgets();
  }

  // Export for manual initialization if needed
  window.initializeMultiUploadWidget = initializeMultiUploadWidget;
})();

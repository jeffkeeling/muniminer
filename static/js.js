$(document).ready(function(){

    //populate dropdown with custom profiles
    for (var key in localStorage){
       $('.profile-dropdown option').first().after(
            "<option data-custom='true' value='" + key + "'>" + key + "</option>"
        );
    }

    var dragOver = function(e) {
        e.preventDefault();
        e.stopPropagation();
        $('#pdf-container').addClass('hovered');
    };

    var dragLeave = function(e) {
        e.preventDefault();
        e.stopPropagation();
        $('#pdf-container').removeClass('hovered');
    };

    var dropFile = function(e) {
        e.preventDefault();
        e.stopPropagation();
        var files = e.originalEvent.dataTransfer.files,
            mimeType= files[0].type; 
        $('#pdf-container').removeClass('hovered');
    
        if (mimeType !== 'application/pdf') {
            return;
        }
    
        $('input[name="pdfFile"]').prop('files', files);
    };

    var checkPdfPresent = function(e) {
        if ( $('input[name="pdfFile"]').val() ){
            $('#pdf-container > p:first-child').addClass('valid');
            return true;
        } else {
            $('#pdf-container > p:first-child').removeClass('valid');
            return false;
        }
    };

    var checkProfilePresent = function(e) {
        if($('.profile-dropdown').val() !== 'default' || 
                ($('.customProfileRegex').val() && $('input[name="customProfile"]').val()) ){
            $('#profile-container > p:first-child').addClass('valid');
            return true;
        } else {
            $('#profile-container > p:first-child').removeClass('valid');
            return false;
        }
    };

    var checkForm = function(e) {
        checkProfilePresent();
        if ( checkPdfPresent() && checkProfilePresent() ){
            $('input[type="submit"]').attr("disabled", false).removeClass('disabledButton');
        } else {
            $('input[type="submit"]').attr("disabled", true).addClass('disabledButton');
        }
    };

    var submitForm = function(e) {
        e.preventDefault();
        var file = $('input[name="pdfFile"]').val(),
            data = new FormData();
        
        data.append('myfile', $('input[name="pdfFile"]')[0].files[0]);
        
        if ($('.profile-dropdown').val() !== 'default') {
            if($('.profile-dropdown').find(':selected').data('custom')) {
                var localStorageRegex = localStorage.getItem($('.profile-dropdown').val() );
                data.append('profileRegex', localStorageRegex);
            } else {
                data.append('profileName', $('.profile-dropdown').val());
            }
            
        } else {
            var nameVal = $('input[name="customProfile"]').val();
            var regexVal = $('.customProfileRegex').val()
            data.append('profileRegex', regexVal);

            localStorage.setItem(nameVal, regexVal);
        }
        $.ajax({
            url: '/upload',
            type: 'POST',
            data: data,
            cache: false,
            processData: false, // Don't process the files
            contentType: false, // Set content type to false as jQuery will tell the server its a query string request
            success: function(data, textStatus, jqXHR)
            {
                $('form').remove();
                $('nav ul').prepend('<li><a class="" href="/">&#171; New PDF</a></li>');
                $('header').after(
                    "<div>" + data + "</div"
                );
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                console.log(jqXHR);
                console.log('ERRORS: ' + textStatus);
            }
        });
    };

    var saveProfiles = function() {
        localStorage.clear();
        $('input.profile-name').each(function(index,data) {
           var nameVal = $(this).val();
           var regexVal =  $(this).parent().siblings('div').find('textarea').val();
           localStorage.setItem(nameVal, regexVal);
        });
        
    };

    var deleteProfile = function(e) {
        var originalName = $(e.currentTarget).siblings('div').find('input').data('originalkey');
        localStorage.removeItem(originalName);
        $(e.currentTarget).parent().remove();
    };
    var profileChanged = function(e) {
        $('.save-profiles').attr("disabled", false).removeClass('disabledButton');
    };

    //event listeners
    $('#pdf-container').on('dragover', dragOver);
    $('#pdf-container').on('dragleave', dragLeave);
    $('#pdf-container').on('drop', dropFile);
    $('input[name="pdfFile"]').on('change', checkForm);
    $('.profile-dropdown').on('change', checkForm);
    $('.customProfileRegex').on('keyup', checkForm);
    $('input[name="customProfile"]').on('keyup', checkForm);
    $("form").submit(submitForm);
    $(".save-profiles").on('click', saveProfiles);
    


    for (var key in localStorage) {
        $('nav ul').append('<li><a href="/edit-profiles">Edit Custom Profiles</a></li>');
        break;
    }

    if(window.location.pathname === '/') {
        options = {

            // Required. Called when a user selects an item in the Chooser.
            success: function(files) {
                console.log(files);
                $('input[name="pdfFile"]').prop('files', files[0].link);
            },

            // Optional. Called when the user closes the dialog without selecting a file
            // and does not include any parameters.
            cancel: function() {

            },

            // Optional. "preview" (default) is a preview link to the document for sharing,
            // "direct" is an expiring link to download the contents of the file. For more
            // information about link types, see Link types below.
            linkType: "direct", // or "direct"

            // Optional. A value of false (default) limits selection to a single file, while
            // true enables multiple file selection.
            multiselect: false, // or true

            // Optional. This is a list of file extensions. If specified, the user will
            // only be able to select files with these extensions. You may also specify
            // file types, such as "video" or "images" in the list. For more information,
            // see File types below. By default, all extensions are allowed.
            extensions: ['.pdf'],
        };
        var button = Dropbox.createChooseButton(options);
        $('.dropbox-container').html(button);
    }

    if(window.location.pathname === '/edit-profiles') {
        var $listContainer = $('.profile-list');
        for (var key in localStorage) {
            $listContainer.append(
                "<li><div><input class='profile-name' data-originalkey='" + key + "' value=" + key + "/></div><div><textarea>" + localStorage[key] + "</textarea></div><span class='delete-profile'>&times;</span></li>"
            );
        }
        $('.delete-profile').on('click', deleteProfile);
        $('input').on('keyup', profileChanged);
        $('textarea').on('keyup', profileChanged);
    }

});
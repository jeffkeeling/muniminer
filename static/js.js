(function($, window, document) {
    $(function() {
        //event listeners
        $('#pdf-container').on('dragover', dragOver).
            on('dragleave', dragLeave).
            on('drop', dropFile);
        $('#pdf-input').on('change', pdfChanged);
        $('#profile-dropdown').on('change', profileDropdownChanged);
        $('#custom-profile-name').on('keyup change', customNameChanged);
        $('#custom-profile-regex').on('keyup change', customRegexChanged);
        $("form").submit(submitForm);
        $("#save-profiles").on('click', saveProfiles);
        $('#add-new-profile').on('click', addNewProfile);
        $('#submit-full-text').on('click', getFullText);

        if(window.location.pathname === '/') {
            //populate dropdown with custom profiles
            var profileHolder = '',
                key;

            for (key in localStorage){
                profileHolder +=  $('#base-container option').clone().
                    attr('value', key).html(key).wrap('<div/>').parent().html();
            }

            //place custom profiles after default
            if (profileHolder.length > 0) {
                $('#profile-dropdown option').first().after(profileHolder);
            }
        }

        if(window.location.pathname === '/edit-profiles') {
            var $listContainer = $('#edit-profile-list'),
                profileHolder = '',
                key;

            for (key in localStorage) {
                profileHolder += $('#base-container li').clone().
                    find('input').attr({'value': key, 'data-originalkey': key}).end().
                    find('textarea').html(localStorage[key]).end().
                    find('.delete-profile').attr('data-originalkey', key).end().
                    wrap('<div/>').parent().html();
            }
            if (profileHolder.length > 0) {
                $listContainer.append(profileHolder);
            }

            $listContainer.on('click', '.delete-profile', deleteProfile).
                on('keyup change', 'input', editProfileChanged).
                on('keyup change', 'textarea', editProfileChanged);
        }
    });

    var formObj = {
        pdf: false,
        profileDropdown: false,
        profileName: false,
        profileRegex: false
    }

    var formObjChanged = function() {
        $('.error').hide();
        if ( formObj.pdf && (formObj.profileDropdown || (formObj.profileName && formObj.profileRegex)) ){
            $('#submit-form').attr("disabled", false).removeClass('disabled-button');
        } else {
            $('#submit-form').attr("disabled", true).addClass('disabled-button');
        }
    }

    $(formObj).on('change', formObjChanged);

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
            $('#pdf-error').html("Provided file not a .pdf document").show();
            return;
        }
    
        $('#pdf-input').prop('files', files);
    };

    var pdfChanged = function(e) {
        if ( $(e.currentTarget).val() ){
            $('#pdf-instruction').addClass('valid');
            $('#submit-full-text').attr("disabled", false).removeClass('disabled-button');
            formObj.pdf = true;
        } else {
            $('#pdf-instruction').removeClass('valid');
            $('#submit-full-text').attr("disabled", true).addClass('disabled-button');
            formObj.pdf = false;
        }
        $(formObj).trigger('change');
    };

    var profileDropdownChanged = function(e) {
        if ($(e.currentTarget).val() !== 'default') {
            $('#profile-instruction').addClass('valid');
            $('#custom-profile-regex').val('')
            $('#custom-profile-name').val('');
            formObj.profileDropdown = true;
            formObj.profileName = false;
            formObj.profileRegex = false;
        } else {
            $('#profile-instruction').removeClass('valid');
            $('#custom-profile-regex').val('')
            $('#custom-profile-name').val('');
            formObj.profileDropdown = false;
            formObj.profileName = false;
            formObj.profileRegex = false;
        }
        $(formObj).trigger('change');
    };

    var customNameChanged = function (e) {
        if ( $(e.currentTarget).val() ) {
            $('#profile-dropdown').val('default');
            formObj.profileDropdown = false;
            formObj.profileName = true;
        } else {
            formObj.profileName = false;
        }
        customProfileChanged();
    };
    var customRegexChanged = function (e) {
        if ( $(e.currentTarget).val() ){
            $('#profile-dropdown').val('default');
            formObj.profileDropdown = false;
            formObj.profileRegex = true;
        } else {
            formObj.profileRegex = false;
        }
        customProfileChanged()
    };

    var customProfileChanged = function () {
        if (formObj.profileName && formObj.profileRegex) {
            $('#profile-instruction').addClass('valid');
        } else {
            $('#profile-instruction').removeClass('valid');
        }
        $(formObj).trigger('change');
    };    

    var submitForm = function(e) {
        e.preventDefault();
        var data = new FormData(),
            $profileDropdown;
        
        data.append('myfile', $('#pdf-input')[0].files[0]);
        
        if (formObj.profileDropdown) {
            $profileDropdown = $('#profile-dropdown')
            if( $profileDropdown.find(':selected').data('custom') ) {
                var localStorageRegex = localStorage.getItem($profileDropdown.val() );
                data.append('profileRegex', localStorageRegex);
                data.append('profileName', $profileDropdown.val());
            } else {
                data.append('profileName', $profileDropdown.val());
            }
        } else {
            var nameVal = $('#custom-profile-name').val(),
                regexVal = $('#custom-profile-regex').val(),
                key;

            for (key in localStorage) {
                if (key === nameVal) {
                    $('#profile-error').html("Profile name already in use").show();
                    $('#profile-instruction').removeClass('valid');
                    $('#submit-form').attr("disabled", true).addClass('disabled-button');
                    return;
                }
            }
            data.append('profileName', nameVal);
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
                var container = ''
                for (var i in data) {
                    container += '<p class="returned-profile-name">' + i + '</p><pre>' + data[i] + '</pre>'
                }
                $('#form-container').html(container);

            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                console.log(jqXHR)
                console.log(errorThrown);
                $('#pdf-error').html("There was an error: " + textStatus).show();
            }
        });
    };
    var getFullText = function(e) {
        e.preventDefault();
        var data = new FormData();
        data.append('myfile', $('#pdf-input')[0].files[0]);
        $.ajax({
            url: '/full-text',
            type: 'POST',
            data: data,
            cache: false,
            processData: false, // Don't process the files
            contentType: false, // Set content type to false as jQuery will tell the server its a query string request
            success: function(data, textStatus, jqXHR)
            {
                window.open('/static/output.txt', '_blank');
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                console.log(jqXHR)
                console.log(errorThrown);
                $('#pdf-error').html("There was an error: " + textStatus).show();
            }
        });
    }
    /*
    Edit Profiles Page
    */
    var editProfileChanged = function(e) {
        $('#edit-profiles-success').hide();

        var emptyFields = false;
        $('#edit-profile-list input').each(function() {
            if ( $(this).val() === '' ){
                emptyFields = true;
            }
        });
        $('#edit-profile-list textarea').each(function() {
            if ( $(this).val() === '' ){
                emptyFields = true;
            }
        });

        if(!emptyFields) {
            $('#save-profiles').attr("disabled", false).removeClass('disabled-button');
        } else {
            $('#save-profiles').attr("disabled", true).addClass('disabled-button');
        }
    };

    var addNewProfile = function(e) {
        var newProfileContainer = $('#base-container li').clone().
            find('input').attr('data-originalkey', 'false').end().
            find('.delete-profile').attr('data-originalkey', 'false').end().
            wrap('<div/>').parent().html();
        $('#edit-profile-list').append(newProfileContainer);

        $('#edit-profiles-success').hide();
        $('#save-profiles').attr("disabled", true).addClass('disabled-button');
    };
       
    var saveProfiles = function() {
        var nameVal,
            regexVal;

        localStorage.clear();
        $('#edit-profile-list input').each(function(index,data) {
            nameVal = $(this).val();
            $(this).data('originalkey', nameVal);
            regexVal =  $(this).parent().siblings('div').find('textarea').val();
            localStorage.setItem(nameVal, regexVal);
        });
        $('#edit-profiles-success').show();
        $('#save-profiles').attr("disabled", true).addClass('disabled-button');
    };

    var deleteProfile = function(e) {
        var originalName = $(e.currentTarget).data('originalkey');

        if(originalName !== 'false'){
            localStorage.removeItem(originalName);
        }
        $(e.currentTarget).parent().remove();
    };
     
}(window.jQuery, window, document));
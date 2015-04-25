$(document).ready(function(){
    var dragOver = function(e) {
        //$(this.ui.dragable_area).addClass('dropzone-hovered');
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
        var mimeType= e.originalEvent.dataTransfer.files[0].type; 
        $('#pdf-container').removeClass('hovered');
        if (mimeType !== 'application/pdf') {
            return;
        }
        $('input[name="pdfFile"]').prop('files', e.originalEvent.dataTransfer.files);
        
    };
    var checkForm = function(e) {
        //to do: combine checks into one
        //to do: remove check if invalid
        if ( $('input[name="pdfFile"]').val() ){
            $('#pdf-container > p:first-child').addClass('valid');
        }

        if($('.profile-dropdown').val() !== 'default' || 
                ($('.customProfileRegex').val() && $('input[name="customProfile"]').val()) ){
            $('#profile-container > p:first-child').addClass('valid');
        }

        if ( $('input[name="pdfFile"]').val() && 
            ( $('.profile-dropdown').val() !== 'default' || 
                ($('.customProfileRegex').val() && $('input[name="customProfile"]').val()) ) ){
            $('input[type="submit"]').attr("disabled", false).removeClass('disabledButton');
        } else {
            $('input[type="submit"]').attr("disabled", true).addClass('disabledButton');
        }
    }

    $('#pdf-container').on('dragover', dragOver);
    $('#pdf-container').on('dragleave', dragLeave);
    $('#pdf-container').on('drop', dropFile);
    $('input[name="pdfFile"]').on('change', checkForm);
    $('.profile-dropdown').on('change', checkForm);
    $('.customProfileRegex').on('keyup', checkForm);
    $('input[name="customProfile"]').on('keyup', checkForm);

    $("form").submit(function(e){
        e.preventDefault();
        var file = $('input[name="pdfFile"]').val();
        var data = new FormData();
        data.append('myfile', $('input[name="pdfFile"]')[0].files[0]);
        if ($('.profile-dropdown').val() !== 'default') {
            data.append('profileName', $('.profile-dropdown').val());
        } else {
            var nameVal = $('input[name="customProfile"]').val();
            data.append('profileName', nameVal);
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
                console.log(data);
                console.log(textStatus);
                console.log(jqXHR);
                
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                console.log(jqXHR);
                console.log('ERRORS: ' + textStatus);
            }
        });
    });
});
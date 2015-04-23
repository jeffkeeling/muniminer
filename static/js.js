$(document).ready(function(){
    $("form").submit(function(e){
        e.preventDefault();
        var file = $('input[name="pdfFile"]').val();
        console.log(file);
        //method="POST"  enctype="multipart/form-data" action="

        console.log(file);
        $.ajax({
            url: '/upload',
            type: 'POST',
            data: file,
            cache: false,
            processData: false, // Don't process the files
            contentType: false, // Set content type to false as jQuery will tell the server its a query string request
            success: function(data, textStatus, jqXHR)
            {
                console.log('success');
                if(typeof data.error === 'undefined')
                {
                    // Success so call function to process the form
                    submitForm(event, data);
                }
                else
                {
                    // Handle errors here
                    console.log('ERRORS: ' + data.error);
                }
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                console.log(jqXHR);
                // Handle errors here
                console.log('ERRORS: ' + textStatus);
                // STOP LOADING SPINNER
            }
        });
    });
});
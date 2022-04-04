$('#formular').submit(function (e) {
    e.preventDefault();
    var button = $('#sendcomment');
    button.attr('disabled', true);
    var form = $(this).serialize();
    $.ajax({
        type: 'POST',
        url: $(this).attr('action'),
        data: form,
        dataType: 'json',
        success: function (result) {
            button.attr('disabled', false);
            if (result.status = "success") {
                document.getElementById('formular').reset();
                Swal.fire({
                    position: 'top-end',
                    icon: 'success',
                    title: "comment send with success",
                    showConfirmButton: false,
                    timer: 1500
                })
            } else {
                Swal.fire({
                    position: 'top-end',
                    icon: 'error',
                    title: result.message,
                    showConfirmButton: false,
                    timer: 1500
                })
            }

        }
    });

});

$('#formularRegister').submit(function (e) {
    e.preventDefault();
    var button = $('#sendcomment');
    button.attr('disabled', true);
    var form = $(this).serialize();
    $.ajax({
        type: 'POST',
        url: $(this).attr('action'),
        data: form,
        dataType: 'json',
        success: function (result) {
            button.attr('disabled', false);
            if (result.status == "success")
             {
                document.getElementById('formularRegister').reset();
                Swal.fire({
                    position: 'top-end',
                    icon: 'success',
                    title: result.message,
                    showConfirmButton: false,
                    timer: 1500
                })
            } else {
                Swal.fire({
                    position: 'top-end',
                    icon: 'error',
                    title: result.message,
                    showConfirmButton: false,
                    timer: 1500
                })
            }

        }
    });
});

$('#login').submit(function (e) {
    e.preventDefault();
    var button = $('#connexion');
    button.attr('disabled', true);

    var form = $(this).serialize();
    $.ajax({
        type: 'POST',
        url: $(this).attr('action'),
        data: form,
        dataType: 'json',
        success: function (result) {
            button.attr('disabled', false);
            if (result.status == "error") {
                document.getElementById('#login').reset();
                Swal.fire({
                    position: 'top-end',
                    icon: 'error',
                    title: result.status,
                    showConfirmButton: false,
                    timer: 1500
                })
            }

        }
    });
});




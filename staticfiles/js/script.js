/* 
All scripts extend here to all the pages
*/

// 1) If no patient is found
$(document).ready(function () {
    var verify = $('#chk_td').length;
    if (verify == 0) {
        $('#no-data').html('No Patient Found !!');
    }
});

// 2) Real-time clock
setInterval(function () {
    var date = new Date();
    $('#clock').html(
        (date.getHours() < 10 ? '0' : '') + date.getHours() + ':' +
        (date.getMinutes() < 10 ? '0' : '') + date.getMinutes() + ':' +
        (date.getSeconds() < 10 ? '0' : '') + date.getSeconds()
    );
}, 500);

// Email validation (optional use)
function validateEmail(email) {
    var regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

// Main form validation
function validateAll() {
    var name = $('#name').val();
    var age = $('#age').val();
    var gender = $('#gender').val();

    if (name == '') {
        swal('Oops!', 'Name field cannot be empty', 'error');
        return false;
    }

    if (age == '') {
        swal('Oops!', 'Age field cannot be empty', 'error');
        return false;
    }

    if (gender == '') {
        swal('Oops!', 'Gender field cannot be empty', 'error');
        return false;
    }

    return true;
}

$('#btn-add').bind('click', validateAll);

// Allow only letters and spaces in name field
$(document).ready(function () {
    $('input[name="name"]').keyup(function () {
        var letter = $(this).val();
        var allow = letter.replace(/[^a-zA-Z\s]/g, '');
        $(this).val(allow);
    });

    // Prevent leading spaces
    $('input').on('keypress', function (e) {
        if (e.which === 32 && !this.value.length) {
            e.preventDefault();
        }
    });
});

// Remove last name restriction logic
// Removed the block that was limiting to two words

// Email to lowercase automatically
$(document).ready(function () {
    $('#email').keyup(function () {
        this.value = this.value.toLowerCase();
    });
});

// Age validations
$(document).ready(function () {
    $('#age').keyup(function () {
        var age = $(this).val();
        if (age > 100) {
            swal('Denied!', 'The maximum value is 100 years old.', 'error');
            $('#age').val('');
            return false;
        }
    });
});

$('#age').keyup(function () {
    if (!/^[0-9]*$/.test(this.value)) {
        this.value = this.value.replace(/[^0-9]/g, '');
    }
});

$('#age').on("input", function () {
    if (/^0/.test(this.value)) {
        this.value = this.value.replace(/^0/, "");
    }
});

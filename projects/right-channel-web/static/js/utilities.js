$(function() {
	String.prototype.format = function() {
		var s = this;
		for ( var i = 0; i < arguments.length; i++) {
			var reg = new RegExp('\\{' + i + '\\}', 'gm');
			s = s.replace(reg, arguments[i]);
		}

		return s;
	};
});

/*function promptOperationAlert(success, message) {
    if (success) {
    	$('.operation-alert').removeClass('alert-error');
    	$('.operation-alert').addClass('alert-success');
    } else {
    	$('.operation-alert').removeClass('alert-success');
    	$('.operation-alert').addClass('alert-error');
    }
    $('.operation-alert-msg').text(message);
    $('.operation-alert').fadeIn().delay(500).fadeOut();
}*/
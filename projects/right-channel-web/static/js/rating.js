function setRating(movieId, rating) {
	$.ajax({
		type : 'post',
		url : '/api/rating/' + movieId,
		data : {
			rating: rating
		}
	}).done(function() {
		showOperationAlert(true, '评分成功');
	}).fail(function(jqXHR) {
		if (jqXHR.status == 401) { // unauthorized
			$.cookie.raw = true;
			$.cookie('next', window.location.href);
			window.location.href = '/login';
		} else {
			showOperationAlert(false, '评分失败');
		}
	});
}
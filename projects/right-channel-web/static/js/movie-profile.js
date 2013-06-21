$(function() {
    $('.interest-unmarked').on('click', 'button', function(event) {
        var movieId = $(this).attr('data-movie-id');
        var interestType = $(this).attr('data-interest-type');
        $.ajax({
            type : 'POST',
            url : '/api/movie/interest',
            data : {
                movie_id: movieId,
                type: interestType
            }
        }).done(function() {
            $('.interest-unmarked').hide();
            $('.interest-marked').fadeIn();
        }).fail(function(jqXHR) {
            if (jqXHR.status == 401) { // unauthorized
                $.cookie.raw = true;
                $.cookie('next', window.location.href);
                window.location.href = '/login';
            }
        });
    })
});
function markInterest($btn) {
	var movieId = $btn.attr('data-movie-id');
	var interestType = $btn.attr('data-interest-type');
	$.ajax({
		type : 'post',
		url : '/api/interest/' + movieId,
		data : {
			interest_type: interestType
		}
	}).done(function() {
		$btn.parent().children('.marked-hint').show();
		$btn.parent().children('.marked').show();
		$btn.parent().children('.unmarked').hide();
		
		var userInterests = new Array();
		userInterests['to_watch'] = '想看';
		userInterests['watched'] = '看过';
		userInterests['not_interested'] = '没兴趣';
		$btn.parent().children('.marked-hint').text('已标记为' + userInterests[interestType]);
		
		showOperationAlert(true, '已标记为' + userInterests[interestType]);
	}).fail(function(jqXHR) {
		if (jqXHR.status == 401) { // unauthorized
			$.cookie.raw = true;
			$.cookie('next', window.location.href);
			window.location.href = '/login';
		} else {
			showOperationAlert(false, '标记失败');
		}
	});
}

function unmarkInterest($btn) {
	var movieId = $btn.attr('data-movie-id');
	$.ajax({
		type : 'delete',
		url : '/api/interest/' + movieId
	}).done(function() {
		$btn.parent().children('.marked-hint').hide();
		$btn.parent().children('.marked').hide();
		$btn.parent().children('.unmarked').show();
		
		showOperationAlert(true, '取消成功');
	}).fail(function(jqXHR) {
		if (jqXHR.status == 401) { // unauthorized
			$.cookie.raw = true;
			$.cookie('next', window.location.href);
			window.location.href = '/login';
		} else {
			showOperationAlert(false, '取消失败');
		}
	});
}